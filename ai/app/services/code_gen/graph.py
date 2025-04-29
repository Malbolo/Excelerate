import requests
import pandas as pd
import re
import traceback

from dotenv import load_dotenv

from typing import Literal
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END


load_dotenv()

class AgentState(MessagesState):
    command_list: List[str]
    python_code: str
    dataframe: List[pd.DataFrame]
    retry_count: int
    error_msg: dict | None

class CodeGenerator:
    def __init__(self):
        self.cllm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
        self.sllm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0)

    def make_template(self) -> ChatPromptTemplate:
        # 2) 시스템 메시지: df와 파라미터를 받아 필터링 코드를 생성한다는 역할 정의
        system_template = SystemMessagePromptTemplate.from_template(
            "당신은 pandas DataFrame을 조작하는 파이썬 코드를 작성하는 전문가입니다."
        )

        # 3) 휴먼 메시지: start_date, end_date 변수를 받아 df 필터링 함수 코드를 만들어 달라는 요청
        human_template = HumanMessagePromptTemplate.from_template(
            """
사용자의 요청에 따라 DataFrame을 조작하는 함수 코드를 작성하세요.
사용자의 요청은 순서가 있는 여러 개별적인 요청으로 나뉘어져 있습니다.
각 요청에 대해 주석에 번호를 붙여 구분해주세요.
주어진 DataFrame은 다음과 같습니다:
{df}
""" +
# """ 
# 함수는 df_manipulate(df)라는 이름으로 작성되어야 하며, df를 인자로 받아야 합니다.
# 반환값은 필터된 DataFrame이어야 합니다.
# """ +
"""
함수는 df_manipulate(df)라는 이름으로 작성되어야 합니다.
각 필터/변환 단계마다 `intermediate.append(…)` 로 DataFrame을 수집하고,
마지막에는 `return intermediate` 로 리스트를 반환해주세요.
"""
+
"""
설명 없이 오직 코드만 작성해 주세요.

사용자의 요청은 다음과 같습니다:
{input}
            """
        )

        # 4) 두 메시지를 합쳐 PromptTemplate 생성
        prompt = ChatPromptTemplate.from_messages([system_template, human_template])
        return prompt

    def code_gen(self, state: AgentState) -> AgentState:
        """
        주어진 `state`에서 메시지를 가져와
        LLM과 도구를 사용하여 응답 메시지를 생성합니다.

        Args:
            state (AgentState): 메시지 기록과 요약을 포함하는 state.

        Returns:
            MessagesState: 응답 메시지를 포함하는 새로운 state.
        """
        # 메시지를 state에서 가져옵니다.
        df = state['dataframe'][0] # 오리지널 df
        input = state['command_list']

        code_gen_prompt = self.make_template()

        schain = code_gen_prompt | self.sllm
        
        # LLM과 도구를 사용하여 메시지에 대한 응답을 생성합니다.
        response = schain.invoke({'df' : df, 'input' : input})

        # 응답 메시지를 포함하는 새로운 state를 반환합니다.
        return {'messages': [response], 'python_code': response.content}

    def check_code(self, state: AgentState) -> Literal['good', 'bad', 'fail']:
        """
        생성된 코드가 적절한 지 확인하고, 적절하면 END로, 적절하지 않으면 재생성합니다.
        """
        sys = SystemMessagePromptTemplate.from_template(
            """
사용자 요청에 따라 DataFrame을 조작하는 함수 코드가 생성되었습니다.
생성된 파이썬 함수 코드가 적절한 지 확인하세요.
""" + 
# """
# 함수는 df_manipulate(df)라는 이름이고, df를 인자로 받습니다.
# 반환값은 필터된 DataFrame이어야 합니다.
# """ +
"""
함수는 df_manipulate(df)라는 이름으로 작성되어야 합니다.
각 필터/변환 단계마다 `intermediate.append(…)` 로 DataFrame을 수집하고,
마지막에는 `return intermediate` 로 리스트를 반환해주세요.
"""
+
"""
주어진 요청을 정확하게 수행하는 코드라면 good, 아니라면 bad를 반환하세요.
            """
        )

        code = HumanMessagePromptTemplate.from_template(
            """
사용자의 요청:
{command_list}

생성된 코드:
{python_code}
            """
        )

        prompt = ChatPromptTemplate.from_messages([sys, code])
        check_chain = prompt | self.sllm

        # LLM과 도구를 사용하여 메시지에 대한 응답을 생성합니다.
        response = check_chain.invoke({'command_list': state['command_list'],'python_code' : state['python_code']})
        if response.content == 'good':
            return 'good'
        
        # bad일 때 재시도 카운트 체크
        if state["retry_count"] < 2:  
            # 아직 2번 미만 재시도 했으면 재실행
            return "bad"
        else:
            # 3번째 재시도(=retry_count 2에서 bad) 후라면 실패 처리
            return "fail"
        
    def regen(self, state: AgentState) -> AgentState:
        """
        재생성된 코드를 포함하는 새로운 state를 반환합니다.
        """
        # 재시도 카운트 증가
        count = state['retry_count'] + 1

        return {'retry_count': count}

    def error_node(self, state: AgentState) -> dict:
        msg = AIMessage(content="⚠️ 코드 생성이 3회 연속 실패했습니다. 나중에 다시 시도해주세요.")
        return {
            "messages": state["messages"] + [msg]
        }
    
    def _extract_error_info(self, exc: Exception, code_body: str, stage: str ) -> dict:
        """
        Exception과 원본 코드 문자열, 실패 단계를 받아서
        해당 번호 블록(# n.)부터 에러 라인까지의 snippet을 반환합니다.
        """
        tb_last = traceback.extract_tb(exc.__traceback__)[-1]
        raw_lineno = tb_last.lineno

        # 1) code_body를 줄 단위로 분리
        lines = code_body.splitlines()
        total = len(lines)

        # 2) 실제 접근 가능한 index로 clamp (에러 방지)
        #    (1-based lineno → 0-based idx)
        err_idx = min(raw_lineno - 1, total - 1)

        # 3) 블록 시작 주석 찾기
        comment_pattern = re.compile(r"\s*#\s*(\d+)\.")
        block_start = 0
        for idx in range(err_idx, -1, -1):
            if comment_pattern.search(lines[idx]):
                block_start = idx
                break

        # 4) snippet 생성 (block_start 부터 err_idx 까지)
        snippet_lines = []
        for i in range(block_start, err_idx + 1):
            text = lines[i].rstrip()
            prefix = "→" if i == err_idx else "  "
            snippet_lines.append(f"{prefix} {i+1:4d}: {text}")

        snippet = "\n".join(snippet_lines)

        return {
            "error_msg": {
                "stage":   stage,
                "message": str(exc),
                "file":    tb_last.filename,
                "line":    raw_lineno,
                "code":    snippet,
            }
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
            return self._extract_error_info(e, code_body, "exec")

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
            return self._extract_error_info(e, code_body, "invoke")

        # 3) 정상 리턴
        return {
            "dataframe": [df, *dfs],
            "error_msg": None,
        }

    def build(self):
        graph_builder = StateGraph(AgentState)

        graph_builder.add_node('codegen', self.code_gen)
        graph_builder.add_node('regen', self.regen)
        graph_builder.add_node('error', self.error_node)
        graph_builder.add_node('execute', self.execute_code)

        graph_builder.add_edge(START, 'codegen')
        graph_builder.add_conditional_edges(
            'codegen',
            self.check_code,
            {
                'good' : 'execute',
                'bad' : 'regen',
                'fail' : 'error',
            })
        graph_builder.add_edge('regen', 'codegen')
        graph_builder.add_edge('error', 'execute')
        graph_builder.add_edge('execute', END)

        return graph_builder.compile()