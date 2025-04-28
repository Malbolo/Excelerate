import requests
import pandas as pd
import re

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

class CodeGenerator:
    def __init__(self):
        self.cllm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
        self.sllm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0)

    def _make_template(self) -> ChatPromptTemplate:
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

    def _code_gen(self, state: AgentState) -> AgentState:
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

        code_gen_prompt = self._make_template()

        schain = code_gen_prompt | self.sllm
        
        # LLM과 도구를 사용하여 메시지에 대한 응답을 생성합니다.
        response = schain.invoke({'df' : df, 'input' : input})

        # 응답 메시지를 포함하는 새로운 state를 반환합니다.
        return {'messages': [response], 'python_code': response.content}

    def _check_code(self, state: AgentState) -> Literal['good', 'bad', 'fail']:
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
        print(response.content)
        if response.content == 'good':
            return 'good'
        
        # bad일 때 재시도 카운트 체크
        if state["retry_count"] < 2:  
            # 아직 2번 미만 재시도 했으면 재실행
            return "bad"
        else:
            # 3번째 재시도(=retry_count 2에서 bad) 후라면 실패 처리
            return "fail"
        
    def _regen(self, state: AgentState) -> AgentState:
        """
        재생성된 코드를 포함하는 새로운 state를 반환합니다.
        """
        # 재시도 카운트 증가
        count = state['retry_count'] + 1
        print(f"retry count: {count}")

        return {'retry_count': count}

    def _error_node(self, state: AgentState) -> dict:
        msg = AIMessage(content="⚠️ 코드 생성이 3회 연속 실패했습니다. 나중에 다시 시도해주세요.")
        print(msg.content)
        return {
            "messages": state["messages"] + [msg],
            "python_code": ""  # 실패 시 빈 문자열 반환
        }
    
    def _execute_code(self, state: AgentState) -> AgentState:
        """
        1) state.python_code 문자열을 exec으로 정의된 함수로 만들고
        2) state.dataframe을 인자로 실행한 뒤
        3) 결과 DataFrame을 state.dataframe에 덮어씁니다.
        """
        code_str = state["python_code"]
        df = state["dataframe"][0] # 오리지널 df

        fence_pattern = re.compile(r"```(?:python)?\n([\s\S]*?)```", re.IGNORECASE)
        m = fence_pattern.search(code_str)
        code_body = m.group(1) if m else code_str

        # 안전을 위해 최소한의 namespace만 넘겨줍니다.
        namespace: dict = {"pd": pd}

        # code_str 안에 반드시
        # def df_manipulate(df): … return df_filtered
        # 형태의 함수 정의가 있어야 합니다.
        exec(code_body, namespace)

        if "df_manipulate" not in namespace:
            raise RuntimeError("생성된 코드 안에 df_manipulate 함수가 없습니다.")

        # # 이제 방금 정의된 함수 호출
        # result_df = namespace["df_manipulate"](df)

        # # 새 DataFrame을 반환하도록 state 업데이트
        # return {
        #     "dataframe": [df, result_df],
        #     # messages, python_code, command_list, retry_count 등
        #     # 다른 필드는 그대로 유지됩니다.
        # }
        # 함수 호출 → 중간/최종 DataFrame들이 담긴 리스트를 받음
        dfs: list[pd.DataFrame] = namespace["df_manipulate"](df)

        # 원본 df 뒤에 중간 단계들을 모두 붙여서 state에 저장
        return {
            "dataframe": [df, *dfs],
        }

    def build(self):
        graph_builder = StateGraph(AgentState)

        graph_builder.add_node('codegen', self._code_gen)
        graph_builder.add_node('regen', self._regen)
        graph_builder.add_node('error', self._error_node)
        graph_builder.add_node('execute', self._execute_code)

        graph_builder.add_edge(START, 'codegen')
        graph_builder.add_conditional_edges(
            'codegen',
            self._check_code,
            {
                'good' : 'execute',
                'bad' : 'regen',
                'fail' : 'error',
            })
        graph_builder.add_edge('regen', 'codegen')
        graph_builder.add_edge('error', END)
        graph_builder.add_edge('execute', END)

        return graph_builder.compile()