from datetime import datetime
from zoneinfo import ZoneInfo
import time
import pandas as pd
import re
import json

from dotenv import load_dotenv

from typing import Literal
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END

from app.utils.memory_logger import MemoryLogger
from app.services.code_gen.graph_util import extract_error_info, make_code_template, make_classify_template

load_dotenv()

class AgentState(MessagesState):
    command_list: List[str]
    python_code: str
    dataframe: List[pd.DataFrame]
    retry_count: int
    error_msg: dict | None
    logs: List[dict]

class CodeGenerator:
    def __init__(self):
        self.logger = MemoryLogger()
        self.cllm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, callbacks=[self.logger])
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0, callbacks=[self.logger])
        self.sllm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0, callbacks=[self.logger])

    def _wrap_node(self, func, node_name):
        def wrapped(state: AgentState, *args, **kwargs):
            # 1) 이전 로그 복사 (List[Dict])
            prev_logs = state.get("logs", []).copy()
            now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()

            # 2) 노드별 input 추출
            if node_name == "codegen":
                input_data = state.get("command_list")
            elif node_name == "execute":
                input_data = state.get("python_code")
            else:
                input_data = None

            # 3) 실제 노드 실행 & 시간 측정
            start = time.time()
            out_state = func(state, *args, **kwargs)
            duration = time.time() - start

            # 4) 노드별 output·metadata 구성
            if node_name == "codegen":
                output_data = out_state.get("python_code")
                # LLM 메시지에서 메타정보 꺼내기
                msg = out_state["messages"][0]
                metadata = {
                    "model": msg.response_metadata.get("model_name"),
                    "token_usage": msg.response_metadata.get("token_usage"),
                }
            else:
                output_data = None
                metadata = {
                    "duration_s": duration,
                    "error": out_state.get("error_msg"),
                }

            # 5) 새 로그 엔트리
            entry = {
                "node":      node_name,
                "input":     input_data,
                "output":    output_data,
                "timestamp": now,
                "metadata":  metadata,
                "sub_events": [], # 하위 로그 이벤트 추가
            }

            # 6) 이전 state + 새로운 out_state 병합
            merged = {**state, **out_state}
            # 7) logs 키에 prev_logs + 새 엔트리
            merged["logs"] = prev_logs + [entry]

            return merged

        return wrapped

    def _wrap_condition(self, func, name):
        """
        check_code 같은 조건 함수의 결과를 state['logs']에 기록합니다.
        func: (state) -> str 리턴하는 함수
        name: 로그에 사용할 단계 이름
        """
        def wrapped(state: AgentState, *args, **kwargs):
            now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
            # 1) 조건 함수 실행
            result = func(state, *args, **kwargs)
            # 2) 로그 항목 생성
            entry = {
                "node":      name,
                "input":     state.get("python_code"),
                "output":    result,
                "timestamp": now,
                "metadata":  {},  # 필요 시 추가 메타데이터 삽입
            }
            # 3) 로그 추가
            state.setdefault("logs", []).append(entry)
            return result

        return wrapped

    def _log_sub_event(self, state: AgentState, name: str, 
                      input=None, output=None, metadata: dict|None=None):
        """
        state['logs']의 마지막 엔트리에 sub_events를 추가합니다.
        """
        timestamp = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        sub = {
            "event":     name,
            "input":     input,
            "output":    output,
            "metadata":  metadata or {},
            "timestamp": timestamp,
        }
        # 가장 최근에 추가된 노드 로그 엔트리
        if state.get("logs"):
            state["logs"][-1].setdefault("sub_events", []).append(sub)
        return state

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
        llm_entry = self.logger.logs[-1] if self.logger.logs else {}
        # state 업데이트
        new_logs = state.get("logs", []) + [llm_entry]

        # 최종적으로 파이썬 리스트를 state에 넣어 줌
        return {'command_list': new_list, 'logs': new_logs}

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
        df = state['dataframe'][0] # 오리지널 df
        input = state['command_list']

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
        llm_entry = self.logger.logs[-1] if self.logger.logs else {}
        # state 업데이트
        new_logs = state.get("logs", []) + [llm_entry]

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
        return {
            "messages": state["messages"] + [msg]
        }
    
    def execute_code(self, state: AgentState) -> AgentState:
        code_str = state["python_code"]
        df = state["dataframe"][0]

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

        # 3) 정상 리턴
        return {
            "dataframe": [df, *dfs],
            "error_msg": None,
        }

    def build(self):
        graph_builder = StateGraph(AgentState)
        # # 각 메서드를 wrap 하여 노드 추가
        handlers = {
            'group' : self.classify_and_group,
            'codegen': self.code_gen,
            'retry':   self.retry,
            'error':   self.error_node,
            'execute': self.execute_code,
        }

        # 래핑해서 노드로 등록
        for name, fn in handlers.items():
            # graph_builder.add_node(name, self._wrap_node(fn, name))
            graph_builder.add_node(name, fn) # wrap 안하고 노드 추가가

        graph_builder.add_edge(START, 'group')
        graph_builder.add_edge('group', 'codegen')
        graph_builder.add_edge('codegen', 'execute')
        graph_builder.add_conditional_edges(
            "execute",
            # error_msg가 없으면 success, 있으면 retry
            lambda s: "success" if not s.get("error_msg") else "fail",
            {
                "success": END,   # 에러 없으면 종료
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