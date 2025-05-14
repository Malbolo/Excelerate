import re
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)

def make_entity_extraction_prompt() -> ChatPromptTemplate:
    """
    FileAPIClient.__init__에서 쓰이는 FileAPIDetail 객체 추출용 ChatPromptTemplate을 반환합니다.
    """
    system_template = SystemMessagePromptTemplate.from_template("""
오늘은 {today}입니다.
다음 필드를 추출하세요: factory_name, system_name, metric, factory_id, product_code, start_date, end_date.
해당하는 값이 없으면 null로 두세요.
— start_date, end_date 처리 규칙 —
1) '숫자+월+숫자+일' 패턴(예: 4월 15일)만 YYYY-MM-DD 형태로 즉시 변환하여 추출하세요.
2) '지난달', '어제', '3일 전' 등 상대 표현은 절대 변환하지 말고, **원문 그대로** '지난달', '어제' 등으로 추출하세요.
3) end_date를 특정할 수 있는 표현이 없으면 null로 두세요.

<context>
{context}
</context>
""")
    human_template = HumanMessagePromptTemplate.from_template("{input}")
    
    return ChatPromptTemplate.from_messages([system_template, human_template])

def is_iso_date(s: str) -> bool:
    """YYYY-MM-DD 형식인지 간단히 체크"""
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s))

def make_date_code_template() -> ChatPromptTemplate:
    """
    start_expr, end_expr 두 상대 날짜 표현을 받아,
    오늘(date.today()) 기준으로 ISO 8601 형식의 startdate, enddate 변수를 세팅하는
    파이썬 코드 스니펫을 생성하는 템플릿을 반환합니다.
    마지막 줄에는 반드시 startdate, enddate 변수가 ISO 문자열로 설정되어 있어야 합니다.
    출력은 마크다운 없이 코드만 반환합니다.
    """
    system_template = SystemMessagePromptTemplate.from_template(
        "당신은 두 개의 상대 날짜 표현(start_expr, end_expr)을 입력받아, "
        "오늘(date.today())을 기준으로 ISO 8601 형식의 날짜 문자열인 "
        "`startdate`, `enddate` 변수를 생성하는 파이썬 코드를 작성하는 전문가입니다.\n"
        "반환된 코드에는 반드시 `startdate`, `enddate` 변수가 ISO 문자열로 설정되어야 합니다. "
        "출력은 마크다운 없이 순수 코드만 반환해주세요."
    )

    example_h1 = HumanMessagePromptTemplate.from_template("start_expr: 지난달, end_expr: 오늘")
    example_a1 = AIMessagePromptTemplate.from_template(
        """
from datetime import date
from dateutil.relativedelta import relativedelta

today = date.today()
first_of_this = today.replace(day=1)
first_of_last = first_of_this - relativedelta(months=1)
startdate = first_of_last.isoformat()

enddate = today().isoformat()
"""
    )

    human_template = HumanMessagePromptTemplate.from_template("start_expr: {start_expr}, end_expr: {end_expr}")

    return ChatPromptTemplate.from_messages([system_template, example_h1, example_a1, human_template])

