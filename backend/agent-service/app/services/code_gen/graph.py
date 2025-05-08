import pandas as pd
import re
import json
import os

from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing_extensions import List, Dict, Optional, Any
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END

from app.utils.memory_logger import MemoryLogger
from app.services.code_gen.graph_util import (
    extract_error_info, make_code_template, make_classify_template,
    make_extract_excel_params_template, insert_df_to_excel, make_excel_code_snippet
)
from app.utils.minio_client import MinioClient
from tempfile import TemporaryDirectory
from uuid import uuid4
from itsdangerous import TimestampSigner

from app.models.log import LogDetail
from app.core.config import settings

from app.services.code_gen.merge_utils import merge_code_snippets

load_dotenv()

class AgentState(MessagesState):
    command_list: List[str]
    queue_idx: int # 현재 진행중인 큐
    classified_cmds: List[dict] # 타입 분류된 커맨드 리스트
    current_unit: Optional[Dict[str, str]] = Field(None, description="현재 실행 중인 명령 단위(cmd, type)")
    python_code: str
    python_codes_list: List[str] # 각 단계별 코드 리스트 모음
    dataframe: List[pd.DataFrame]
    retry_count: int
    error_msg: dict | None
    logs: List[LogDetail]
    download_token: str

class CodeGenerator:
    def __init__(self):
        self.logger = MemoryLogger()
        self.minio_client = MinioClient()
        self.cllm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, callbacks=[self.logger])
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0, callbacks=[self.logger])
        self.sllm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0, callbacks=[self.logger])

    def classify_and_group(self, state: AgentState) -> AgentState:
        """
        1) 사용자 커맨드 리스트를 LLM에 넘겨
           [{'command': ..., 'type': 'df'|'excel'}, ...] 형태로 분류
        2) 실패 시 모든 명령을 'df'로 간주
        """
        # 로그 이름 설정 & 초기화
        self.logger.set_name("LLM Call: Split Command List")
        self.logger.reset()

        prev_cls = state.get("classified_cmds", [])
        all_cmds = state["command_list"]

        # 1) 이전에 처리된 커맨드 수(processed_count) 계산
        processed_count = 0
        for entry in prev_cls:
            raw = entry.get("cmd")
            # raw가 실제 list면 그대로, str이면 JSON 파싱 시도
            if isinstance(raw, list):
                cmd_list = raw
            elif isinstance(raw, str) and raw.strip().startswith("["):
                try:
                    parsed = json.loads(raw)
                    cmd_list = parsed if isinstance(parsed, list) else [raw]
                except json.JSONDecodeError:
                    cmd_list = [raw]
            else:
                cmd_list = [raw]

            processed_count += len(cmd_list)

        # 2) 건너뛸 커맨드 수만큼 앞부분 스킵 → 신규 명령어 목록
        new_cmds = all_cmds[processed_count:]

        # 3) 신규가 없으면 건너뛰기
        if not new_cmds:
            return {
                "classified_cmds": prev_cls,
                "queue_idx":       state["queue_idx"],
                "logs":            state.get("logs", [])
            }

        cmds = new_cmds
        prompt = make_classify_template()
        # invoke
        cng_chain = prompt | self.sllm
        resp = cng_chain.invoke({"cmd_list": json.dumps(cmds, ensure_ascii=False)})
        
        # 5. 응답 파싱 & 검증
        classified: list[dict] = []
        try:
            parsed = json.loads(resp.content)
            if not isinstance(parsed, list):
                raise ValueError("Expected a JSON list")

            for item in parsed:
                cmd = item.get("command")
                typ = item.get("type")
                if not cmd or typ not in ("df", "excel"):
                    raise ValueError(f"Invalid item: {item}")
                classified.append({"cmd": cmd, "type": typ})

        except Exception:
            # 파싱 실패 시, 모든 명령을 df로 처리
            classified = [{"cmd": c, "type": "df"} for c in cmds]

        # 로깅 추출
        llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
        new_logs  = state.get("logs", []) + ([llm_entry] if llm_entry else [])

        # State 업데이트
        return {
            "classified_cmds": prev_cls+ classified,
            "queue_idx":       state["queue_idx"],
            "logs":            new_logs
        }

    def next_unit(self, state: AgentState) -> AgentState:
        """
        classified_cmds 리스트에서 queue_idx 위치의 유닛을 꺼내
        state["current_unit"]에 담고,
        queue_idx는 +1, retry_count는 0으로 초기화하여 반환.
        """
        classified = state["classified_cmds"]
        idx        = state.get("queue_idx", 0)

        # 1) 남은 명령이 없으면 종료 플래그 세팅
        if idx >= len(classified):
            return {"current_unit" : {"type":"done"}}

        # 2) 현재 유닛 꺼내기
        unit = classified[idx]
        #    unit == {"cmd": "...", "type": "df" or "excel"}

        # 3) 다음 인덱스와 retry_count 초기화
        new_state = {
            **state,
            "current_unit": unit,
            "queue_idx":    idx + 1,
            "retry_count":  0
        }
        return new_state

    def code_gen(self, state: AgentState) -> AgentState:
        """
        주어진 `state`에서 메시지를 가져와
        LLM과 도구를 사용하여 응답 메시지를 생성합니다.

        Args:
            state (AgentState): 메시지 기록과 요약을 포함하는 state.

        Returns:
            MessagesState: 응답 메시지를 포함하는 새로운 state.
        """
        # 로그 이름 설정 & 초기화
        self.logger.set_name("LLM Call: Generate Code")
        self.logger.reset()

        # 메시지를 state에서 가져옵니다.
        df = state['dataframe'][-1] # 마지막 df
        input = state["current_unit"]["cmd"]

        code_gen_prompt = make_code_template()

        schain = code_gen_prompt | self.sllm
        
        # LLM과 도구를 사용하여 메시지에 대한 응답을 생성합니다.
        # 1) LLM 호출 전 input 준비
        df_preview = df.head(5).to_string(
            index=False,          # 인덱스 번호 제거
            show_dimensions=False # 맨 마지막 shape 요약 생략
        )

        llm_input = {"dftypes": df.dtypes.to_string(), "df": df_preview, "input": input}

        # 2) LLM 호출
        response = schain.invoke(llm_input)

        # 가장 마지막 LLM 로그 항목 추출
        llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
        # state 업데이트
        new_logs = state.get("logs", []) + [llm_entry] if llm_entry else state.get("logs", [])

        # 응답 메시지를 포함하는 새로운 state를 반환합니다.
        return {'messages': [response], 'python_code': response.content, 'logs': new_logs}
        
    def retry(self, state: AgentState) -> AgentState:
        """
        error_msg를 초기화하고
        재생성된 카운트를 늘려 새로운 state를 반환합니다.
        """
        # 재시도 카운트 증가
        count = state['retry_count'] + 1
        if count > 3:
            return {'retry_count': count}

        return {'error_msg': None, 'retry_count': count}

    def error_node(self, state: AgentState) -> AgentState:
        msg = AIMessage(content="⚠️ 코드 생성이 3회 연속 실패했습니다. 나중에 다시 시도해주세요.")
        # 에러 시 처리 코드 추가
        return {
            "messages": state["messages"] + [msg]
        }
    
    def execute_code(self, state: AgentState) -> AgentState:
        code_str = state["python_code"]
        df = state["dataframe"][-1]

        fence_pattern = re.compile(r"```(?:python)?\n([\s\S]*?)```", re.IGNORECASE)
        m = fence_pattern.search(code_str)
        code_body = m.group(1) if m else code_str

        namespace: dict = {"pd": pd, "df": df}

        # 1) exec 단계
        try:
            compiled = compile(code_body, "<user_code>", "exec")
            exec(compiled, namespace)
        except Exception as e:
            # 위치 인자로만 stage를 넘김
            return extract_error_info(e, code_body, "exec")

        # 2) invoke 단계 → 스크립트 실행 직후 intermediate 변수에서 결과 목록 추출
        try:
            # 스크립트 안에서 df와 intermediate 변수가 정의됨
            dfs: list[pd.DataFrame] = namespace.get("intermediate")
            if not isinstance(dfs, list):
                raise ValueError("`intermediate` 리스트가 없습니다.")
        except Exception as e:
            return extract_error_info(e, code_body, "invoke")
        
        # 3) dataframes와 codes 갱신
        new_dataframes = state.get("dataframe", []) + dfs
        codes = state.get("python_codes_list", []) + [code_str]

        merged_code = merge_code_snippets(codes)

        # 4) 정상 리턴
        return {
            "python_code": merged_code,
            "dataframe": new_dataframes,
            "error_msg": None,
            "python_codes_list": codes,
        }

    def excel_manipulate(self, state: AgentState) -> AgentState:
        """
        'excel' 타입 명령 처리:
        - 커맨드에서 템플릿 이름 추출
        - MinIO에서 템플릿 다운로드
        - 마지막 DataFrame을 템플릿에 삽입
        - 결과 엑셀을 MinIO에 업로드하고 presigned URL 반환
        """
        self.logger.set_name("LLM Call: Manipulate Excel")
        self.logger.reset()
        unit = state['current_unit']
        cmd = unit.get("cmd", "")

        prompt = make_extract_excel_params_template()
        params = json.loads((prompt | self.sllm).invoke({"command": str(cmd)}).content)

        with TemporaryDirectory() as workdir:
            tpl_path = f"{workdir}/template.xlsx"
            out_path = f"{workdir}/result.xlsx"

            self.minio_client.download_template(params["template_name"], tpl_path)
            df = state["dataframe"][-1]
            insert_df_to_excel(
                df,
                input_path=tpl_path,
                output_path=out_path,
                sheet_name=params.get("sheet_name"),
                start_row=params["start_row"],
                start_col=params["start_col"]
            )
            # url = self.minio_client.upload_result(user_id="test", template_name=params["output_name"], local_path=out_path)
            uid        = uuid4().hex
            file_name  = f"{params['template_name']}_{uid}.xlsx"
            object_key = f"outputs/{file_name}"
            self.minio_client.upload_excel(object_key, out_path)
            signer = TimestampSigner(settings.TOKEN_SECRET_KEY)
            token = signer.sign(object_key.encode()).decode()

        code_snippet = make_excel_code_snippet(
            template_name=params['template_name'],
            output_name=params['output_name'],
            start_row=params['start_row'],
            start_col=params['start_col'],
            sheet_name=params.get('sheet_name'),
            user_id="auto"
        )

        codes = state.get("python_codes_list", []) + [code_snippet]

        merged_code = merge_code_snippets(codes)

        # 가장 마지막 LLM 로그 항목 추출
        llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
        # state 업데이트
        new_logs = state.get("logs", []) + [llm_entry] if llm_entry else state.get("logs", [])

        return {"download_token": token, "error_msg": None, "logs": new_logs, "python_code":merged_code, "python_codes_list": codes}

    def build(self):
        graph_builder = StateGraph(AgentState)
        handlers = {
            'split' : self.classify_and_group,
            'next_unit' : self.next_unit,
            'codegen': self.code_gen,
            'retry':   self.retry,
            'error':   self.error_node,
            'execute': self.execute_code,
            'excel_manipulate': self.excel_manipulate
        }
        # 노드로 등록
        for name, fn in handlers.items():
            # graph_builder.add_node(name, self._wrap_node(fn, name)) # 각 메서드를 wrap 하여 노드 추가
            graph_builder.add_node(name, fn) # wrap 안하고 노드 추가가

        graph_builder.add_edge(START, 'split')
        graph_builder.add_edge('split', 'next_unit')

        # next_unit 단계: 완료 여부 및 타입(df/excel) 따라 분기
        graph_builder.add_conditional_edges(
            'next_unit',
            lambda state: state['current_unit'].get('type'),
            {
                'done': END,
                'df': 'codegen',
                'excel': 'excel_manipulate'
            }
        )

        # DataFrame 코드 생성 → 실행 → 분기 처리
        graph_builder.add_edge('codegen', 'execute')
        graph_builder.add_conditional_edges(
            'execute',
            # error_msg 유무 + retry_count 체크로 분기
            lambda state: (
                'success' if state['error_msg'] is None
                else 'retry' if state['retry_count'] < 3
                else 'error'
            ),
            {
                'success': 'next_unit',
                'retry':   'retry',
                'error':   'error'
            }
        )

        # 재시도 로직: retry 횟수 증가 후 재코드 생성
        graph_builder.add_edge('retry', 'codegen')

        # excel_manipulate 처리 후 다음 명령으로 복귀
        graph_builder.add_edge('excel_manipulate', 'next_unit')

        # 오류 노드 → 종료
        graph_builder.add_edge('error', END)

        return graph_builder.compile()
