import os
import pandas as pd
import re
import json

from dotenv import load_dotenv

from pydantic import Field
from typing_extensions import List, Dict, Optional
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END

from tempfile import mkdtemp
from itsdangerous import TimestampSigner

from app.core.config import settings
from app.models.log import LogDetail
from app.utils.minio_client import MinioClient

from app.services.code_gen.graph_util import ( 
    extract_error_info, insert_df_to_excel,
    log_filter, extract_relevant_code_fuzzy
)
from app.services.code_gen.merge_utils import merge_code_snippets

from app.utils.memory_logger import MemoryLogger
from app.utils.api_utils import get_log_queue, get_df_queue
from app.utils.chatprompt.redis_chatprompt import load_chat_template

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
    stream_id: str
    original_code: str | None

class CodeGenerator:
    def __init__(self):
        self.logger = MemoryLogger()
        self.minio_client = MinioClient()
        self.sllm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0, callbacks=[self.logger])
        self.q = None

    def classify_and_group(self, state: AgentState) -> AgentState:
        """
        1) 사용자 커맨드 리스트를 LLM에 넘겨
           [{'command': ..., 'type': 'df'|'excel|'none''}, ...] 형태로 분류
        2) 실패 시 모든 명령을 'none'으로 간주
        """
        # 로그 이름 설정 & 초기화
        self.logger.set_name("LLM Call: Split Command List")
        self.logger.reset()
        self.q = get_log_queue(state["stream_id"])
        self.q.put_nowait({"type": "notice", "content": "커맨드 리스트를 분류하고 있습니다."})

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
        prompt = load_chat_template("Code Generator:Split Command List")
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
                if not cmd or typ not in ("df", "excel", "none"):
                    raise ValueError(f"Invalid item: {item}")
                classified.append({"cmd": cmd, "type": typ})

        except Exception:
            # 파싱 실패 시, 모든 명령을 none으로 처리
            classified = [{"cmd": c, "type": "none"} for c in cmds]

        # 로깅 추출
        llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
        new_logs  = state.get("logs", []) + ([llm_entry] if llm_entry else [])

        # stream_id로 쏘기
        if llm_entry:
            log = log_filter(llm_entry)
            self.q.put_nowait({"type": "log", "content": log})

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

    def none_handler(self, state: AgentState) -> AgentState:
        """
        'none' 타입 명령 처리: 코드에 주석 추가 후 다음 유닛으로 스킵
        """
        unit = state['current_unit']
        cmd = unit.get('cmd', '')

        # none 타입도 코드 생성 로직을 추가해야할까 고민
        comment = f"# {cmd}"
        
        codes = state.get('python_codes_list', []) + [comment]
        merged = merge_code_snippets(codes)
        self.q.put_nowait({"type": "notice", "content": f"{cmd} -> none 타입 명령으로 처리합니다."})
        self.q.put_nowait({"type": "codes", "content": merged})
        return {"python_codes_list": codes, "python_code": merged}

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
        self.q.put_nowait({"type": "notice", "content": f"{input}에 대한 코드를 생성 중입니다."})

        # input str → 리스트로 만들기
        if isinstance(input, str):
            try:
                cmds_list = json.loads(input)
                # 만약 단일 문자열이라면 리스트로 감싸기
                if not isinstance(cmds_list, list):
                    cmds_list = [cmds_list]
            except json.JSONDecodeError:
                cmds_list = [input]
        elif isinstance(input, list):
            cmds_list = input
        else:
            cmds_list = [str(input)]

        # LLM과 도구를 사용하여 메시지에 대한 응답을 생성합니다.
        # 1) LLM 호출 전 input 준비
        df_preview = df.head(5).to_string(
            index=False,          # 인덱스 번호 제거
            show_dimensions=False # 맨 마지막 shape 요약 생략
        )

        if state['original_code']:
            self.q.put_nowait({"type": "notice", "content": f"{input}에 대한 코드를 기존 코드와 함께 생성 중입니다."})
            relevant_snippet = extract_relevant_code_fuzzy(
                state['original_code'],
                cmds_list,
                similarity_threshold=0.7
            ) # cmds_list와 70% 이상 유사한 블럭만 참고로 넣음
            original_for_prompt = relevant_snippet
            code_gen_prompt = load_chat_template("Code Generator:Generate Code Extension")
            schain = code_gen_prompt | self.sllm
            llm_input = {"original_code":original_for_prompt, "dftypes": df.dtypes.to_string(), "df": df_preview, "input": input}
        else:
            code_gen_prompt = load_chat_template("Code Generator:Generate Code")
            schain = code_gen_prompt | self.sllm
            llm_input = {"dftypes": df.dtypes.to_string(), "df": df_preview, "input": input}

        # 2) LLM 호출
        response = schain.invoke(llm_input)

        # 가장 마지막 LLM 로그 항목 추출
        llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
        # state 업데이트
        new_logs = state.get("logs", []) + [llm_entry] if llm_entry else state.get("logs", [])

        # stream_id로 쏘기
        if llm_entry:
            log = log_filter(llm_entry)
            self.q.put_nowait({"type": "log", "content": log})

        # 응답 메시지를 포함하는 새로운 state를 반환합니다.
        return {'python_code': response.content, 'logs': new_logs}
        
    def retry(self, state: AgentState) -> AgentState:
        """
        error_msg를 초기화하고
        재생성된 카운트를 늘려 새로운 state를 반환합니다.
        """
        # 재시도 카운트 증가
        count = state['retry_count'] + 1
        if count > 3:
            self.q.put_nowait({"type": "notice", "content": "코드 생성에 실패해 재 생성 중..."})
            return {'retry_count': count}

        return {'error_msg': None, 'retry_count': count}

    def error_node(self, state: AgentState) -> AgentState:
        msg = AIMessage(content="⚠️ 코드 생성이 3회 연속 실패했습니다. 나중에 다시 시도해주세요.")
        self.q.put_nowait({"type": "notice", "content": "⚠️ 코드 생성이 3회 연속 실패했습니다."})
        # 에러 시 생성된 코드 리스트 합쳐서 반환
        code_str = state["python_code"]
        codes = state.get("python_codes_list", []) + [code_str]

        merged_code = merge_code_snippets(codes)

        self.q.put_nowait({"type": "code", "content": merged_code})
        return {
            "messages": state["messages"] + [msg],
            "python_code": merged_code,
        }
    
    def execute_code(self, state: AgentState) -> AgentState:
        code_str = state["python_code"]
        df = state["dataframe"][-1]

        commands = state["command_list"]
        self.q.put_nowait({"type": "notice", "content": "생성된 코드를 실행 중입니다."})

        fence_pattern = re.compile(r"```(?:python)?\n([\s\S]*?)```", re.IGNORECASE)
        m = fence_pattern.search(code_str)
        code_body = m.group(1) if m else code_str

        namespace: dict = {"pd": pd, "df": df}

        # 1) exec 단계
        try:
            compiled = compile(code_body, "<user_code>", "exec")
            exec(compiled, namespace)
        except Exception as e:
            self.q.put_nowait({"type": "notice", "content": "코드를 실행 중 에러가 발생했습니다."})
            return extract_error_info(e, code_body, "exec", commands)

        # 2) invoke 단계 → 스크립트 실행 직후 intermediate 변수에서 결과 목록 추출
        try:
            # 스크립트 안에서 df와 intermediate 변수가 정의됨
            dfs: list[pd.DataFrame] = namespace.get("intermediate")
            if not isinstance(dfs, list):
                raise ValueError("`intermediate` 리스트가 없습니다.")
        except Exception as e:
            self.q.put_nowait({"type": "notice", "content": "결과 추출 중 에러가 발생했습니다."})
            return extract_error_info(e, code_body, "invoke", commands)
        
        # 3) dataframes와 codes 갱신
        new_dataframes = state.get("dataframe", []) + dfs
        codes = state.get("python_codes_list", []) + [code_str]

        merged_code = merge_code_snippets(codes)

        self.q.put_nowait({"type": "notice", "content": "코드가 정상적으로 실행되었습니다."})
        self.q.put_nowait({"type": "code", "content": merged_code})

        # self.q.put_nowait({"type": "data", "content": dfs[-1]})
        df_q = get_df_queue(state["stream_id"])
        for df in dfs:
            df_q.put_nowait(df)

        # 4) 정상 리턴
        return {
            "python_code": merged_code,
            "dataframe": new_dataframes,
            "error_msg": None,
            "python_codes_list": codes,
        }

    def excel_generate(self, state: AgentState) -> AgentState:
        """
        'excel' 타입 명령을 처리하는 코드 생성:
        - 커맨드에서 템플릿 이름 추출
        - MinIO에서 템플릿 다운로드
        - 마지막 DataFrame을 템플릿에 삽입
        """
        self.logger.set_name("LLM Call: Manipulate Excel")
        self.logger.reset()
        unit = state['current_unit']
        cmd = unit.get("cmd", "")

        self.q.put_nowait({"type": "notice", "content": f"엑셀 작업 코드를 생성합니다."})
        prompt   = load_chat_template("Code Generator:Manipulate Excel")
        schain   = prompt | self.sllm
        response = schain.invoke({"input": cmd})
        code_str = response.content

        # 가장 마지막 LLM 로그 항목 추출
        llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
        # state 업데이트
        new_logs = state.get("logs", []) + [llm_entry] if llm_entry else state.get("logs", [])

        # stream_id로 쏘기
        if llm_entry:
            log = log_filter(llm_entry)
            self.q.put_nowait({"type": "notice", "content": "엑셀 코드를 생성하였습니다."})
            self.q.put_nowait({"type": "log", "content": log})

        return {"python_code": code_str, "logs": new_logs}

    def excel_execute(self, state: AgentState) -> AgentState:
        code_str = state["python_code"]
        df = state["dataframe"][-1]

        fence_pattern = re.compile(r"```(?:python)?\n([\s\S]*?)```", re.IGNORECASE)
        m = fence_pattern.search(code_str)
        code_body = m.group(1) if m else code_str
        
        namespace = {
            "pd": pd,
            "df": df,
            "insert_df_to_excel": insert_df_to_excel,
            "MinioClient": MinioClient,
            "mkdtemp": mkdtemp,
            "os": os,
        }

        # exec
        try:
            compiled = compile(code_body, "<user_code>", "exec")
            exec(compiled, namespace)
        except Exception as e:
            self.q.put_nowait({"type": "notice", "content": "코드를 실행 중 에러가 발생했습니다."})
            commands = state["command_list"]
            return extract_error_info(e, code_body, "exec", commands)

        out = namespace.get("out")

        if out:
            file_name   = os.path.basename(out)
            object_key = f"outputs/{file_name}"
            try:
                self.minio_client.upload_excel(object_key, out)
                signer = TimestampSigner(settings.TOKEN_SECRET_KEY)
                token = signer.sign(object_key.encode()).decode()
            except:
                self.q.put_nowait({"type": "notice", "content": "엑셀 파일 업로드 중 에러가 발생했습니다."})
                token = None
        
        # temp 파일 삭제

        codes = state.get("python_codes_list", []) + [code_body]

        merged_code = merge_code_snippets(codes)

        # stream_id로 쏘기
        self.q.put_nowait({"type": "notice", "content": "엑셀 파일을 생성하였습니다."})
        self.q.put_nowait({"type": "code", "content": merged_code})

        return {"download_token": token, "error_msg": None, "python_code":merged_code, "python_codes_list": codes}

    def build(self):
        graph_builder = StateGraph(AgentState)
        handlers = {
            'split' : self.classify_and_group,
            'next_unit' : self.next_unit,
            'none_handler': self.none_handler,
            'codegen': self.code_gen,
            'retry':   self.retry,
            'error':   self.error_node,
            'execute': self.execute_code,
            'excel_generate': self.excel_generate,
            'excel_execute': self.excel_execute
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
                'excel': 'excel_generate',
                'none': 'none_handler'
            }
        )

        graph_builder.add_edge('none_handler', 'next_unit')

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
        graph_builder.add_edge('excel_generate', 'excel_execute')
        graph_builder.add_conditional_edges(
            'excel_execute',
            # 엑셀 명령은 오류날 시 바로 오류 반환. (파일이 잘못 생성된건 눈으로 확인하기 힘듬)
            lambda state: (
                'success' if state['error_msg'] is None
                else 'error'
            ),
            {
                'success': 'next_unit',
                'error':   'error'
            }
        )

        # 오류 노드 → 종료
        graph_builder.add_edge('error', END)

        return graph_builder.compile()
