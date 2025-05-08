from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

def make_date_code_template() -> ChatPromptTemplate:
    """
    상대 날짜 표현(expr)을 오늘(date.today()) 기준으로 ISO 8601 날짜 문자열로 계산하는
    파이썬 코드 스니펫을 생성하는 템플릿을 반환합니다.
    생성된 코드의 마지막 줄에는 반드시 startdate 변수가 ISO 형식 문자열로 세팅되어야 합니다.
    """
    system_template = SystemMessagePromptTemplate.from_template(
        "당신은 상대 날짜 표현(expr)을 오늘(date.today())을 기준으로 계산하여 "
        "ISO 8601 형식의 날짜 문자열을 생성하는 파이썬 코드를 작성하는 전문가입니다. "
        "반환된 코드의 마지막 줄에는 반드시 `startdate` 변수가 ISO 문자열로 설정되어 있어야 합니다."
    )

    human_template = HumanMessagePromptTemplate.from_template(
        """
다음 상대 날짜 표현(expr)을 오늘(date.today())을 기준으로 계산하는 파이썬 코드로 작성하세요.
마지막 줄에서 반드시:

    startdate = "<ISO 8601 날짜 문자열>"

형태로 `startdate` 변수가 설정되어 있어야 합니다.

예시) expr="지난달"
```python
from datetime import date
from dateutil.relativedelta import relativedelta

today = date.today()
first_of_this = today.replace(day=1)
first_of_last = first_of_this - relativedelta(months=1)
startdate = first_of_last.isoformat()
```
이제 expr="{expr}"에 대해 코드를 작성하세요.
"""
    )
    return ChatPromptTemplate.from_messages([system_template, human_template])

