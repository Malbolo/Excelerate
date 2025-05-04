import pandas as pd
import re
import json
import os

from dotenv import load_dotenv

from typing_extensions import List
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END

from app.utils.memory_logger import MemoryLogger
from app.services.code_gen.graph_util import extract_error_info, make_code_template, make_classify_template, make_excel_template, insert_df_to_excel
from app.utils.minio_client import MinioClient

from app.models.log import LogDetail

load_dotenv()

class AgentState(MessagesState):
    command_list: List[str]
    queue_idx: int # 현재 진행중인 큐
    current_cmds: List[str] # 현재 큐의 커맨드 리스트
    python_code: str
    python_codes_list: List[str] # 각 단계별 코드 리스트 모음
    dataframe: List[pd.DataFrame]
    retry_count: int
    error_msg: dict | None
    logs: List[LogDetail]

class CodeGenerator:
    def __init__(self):
        self.logger = MemoryLogger()
        self.minio_client = MinioClient()
        self.cllm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, callbacks=[self.logger])
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0, callbacks=[self.logger])
        self.sllm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0, callbacks=[self.logger])

        BASE_TEMPLATE_DIR = os.path.dirname(__file__)
        self.file_path = os.path.join(BASE_TEMPLATE_DIR, "test.xlsx")
        self.output_path = os.path.join(BASE_TEMPLATE_DIR, "test_merged.xlsx")

    def classify_and_group(self, state: AgentState) -> AgentState:
        # 로그 이름 설정 & 초기화
        self.logger.set_name("LLM Call: Split Command List")
        self.logger.reset()

        cmds = state['command_list']
        prompt = make_classify_template()
        # invoke
        cng_chain = prompt | self.sllm
        resp = cng_chain.invoke({"cmd_list": json.dumps(cmds, ensure_ascii=False)})
        
        try:
            parsed = json.loads(resp.content)
            # JSON이 리스트가 아니면 에러
            if not isinstance(parsed, list):
                raise ValueError("Not a list")
            # 모든 요소를 문자열로 보장
            new_list = [str(x) for x in parsed]
        except (json.JSONDecodeError, ValueError):
            # 파싱 실패 시 기존 리스트 유지
            new_list = cmds

        # 가장 마지막 LLM 로그 항목 추출
        llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
        # state 업데이트
        new_logs = state.get("logs", []) + [llm_entry] if llm_entry else state.get("logs", [])


        # ########### 겸사겸사 엑셀 조작 테스트
        # print(self.file_path)
        # print(self.output_path)

        # df_sample = state['dataframe'][-1]
        # df_sample.drop("defect_types", axis=1, inplace=True)

        # insert_df_to_excel(
        #     df=df_sample,
        #     input_path=self.file_path,
        #     output_path=self.output_path,
        #     start_row=5,
        #     start_col=2
        # )
        # ########### git에 주석 풀고 올리지 마세요!


        # 커맨드 스플릿, queue_idx 명시적 초기화
        return {'command_list': new_list, 'queue_idx': 0, 'logs': new_logs}

    def next_unit(self, state: AgentState) -> AgentState:
        units = state.get("command_list", []) # 전체 커맨드 리스트
        idx   = state.get("queue_idx", 99) # 현재 처리중인 queue idx

        # 더 처리할 게 없으면 END 분기로
        if idx >= len(units):
            return {"current_cmds": []}

        # 현재 unit 하나 꺼내고, queue_index 증가
        current = units[idx]
        return {
            "current_cmds": [current],   # codegen 이 참조할 리스트
            "queue_idx":   idx + 1, # 이거 증가하는 타이밍을 차후 execute 완료 시로 수정하여, current_cmds 없이 구현
            "retry_count": 0, # 다음으로 넘어가며 retry_count 초기화
        }

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
        input = state["current_cmds"]

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

        namespace: dict = {"pd": pd}

        # 1) exec 단계
        try:
            compiled = compile(code_body, "<user_code>", "exec")
            exec(compiled, namespace)
        except Exception as e:
            # 위치 인자로만 stage를 넘김
            return extract_error_info(e, code_body, "exec")

        # df_manipulate 함수 존재 확인
        if "df_manipulate" not in namespace:
            return {
                "error_msg": {
                    "stage": "validation",
                    "message": "생성된 코드 안에 df_manipulate 함수가 없습니다."
                }
            }

        # 2) invoke 단계
        try:
            dfs: list[pd.DataFrame] = namespace["df_manipulate"](df)
        except Exception as e:
            return extract_error_info(e, code_body, "invoke")
        
        # 3) dataframes와 codes 갱신
        new_dataframes = state.get("dataframe", []) + dfs
        codes = state.get("python_codes_list", []) + [code_str]

        # 4) 정상 리턴
        return {
            "dataframe": new_dataframes,
            "error_msg": None,
            "python_codes_list": codes,
        }

    def excel_manipulate(self, state: AgentState) -> AgentState:
        self.minio_client.download_template(template_name="원본", local_path="/tmp/template.xlsx")
        ## 불러온 템플릿으로 뭔가 수행하기
        ## 수행된 결과 엑셀로 만들기
        url = self.minio_client.upload_result(user_id="tester", template_name="변경", local_path="/tmp/output.xlsx")
        print(url)
        return {}

    def build(self):
        graph_builder = StateGraph(AgentState)
        handlers = {
            'split' : self.classify_and_group,
            'next_unit' : self.next_unit,
            'codegen': self.code_gen,
            'retry':   self.retry,
            'error':   self.error_node,
            'execute': self.execute_code,
        }
        # 노드로 등록
        for name, fn in handlers.items():
            # graph_builder.add_node(name, self._wrap_node(fn, name)) # 각 메서드를 wrap 하여 노드 추가
            graph_builder.add_node(name, fn) # wrap 안하고 노드 추가가

        graph_builder.add_edge(START, 'split')
        graph_builder.add_edge('split', 'next_unit')
        # 남아 있는 cmds가 있으면 수행, 아니면 종료
        graph_builder.add_conditional_edges(
            "next_unit",
            lambda s: "has"  if s.get("current_cmds") else "done",
            {"has": "codegen", "done": END}
        )
        graph_builder.add_edge('codegen', 'execute')
        graph_builder.add_conditional_edges(
            "execute",
            # error_msg가 없으면 success, 있으면 retry
            lambda s: "success" if not s.get("error_msg") else "fail",
            {
                "success": 'next_unit',   # 에러 없으면 다음 커맨드 리스트로
                "fail":   "retry"  # 에러 있으면 retry
            }
        )
        graph_builder.add_conditional_edges(
            'retry',
            # retry_count가 3이상이면 최종 실패
            lambda s: "retry" if not s.get("error_msg") else "fail",
            {
                "retry": 'codegen',
                "fail":   'error'  # 3번 이상 실패했으면 에러로 종료
            }
        )
        graph_builder.add_edge('error', END)

        return graph_builder.compile()