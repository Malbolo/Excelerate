
import re
import traceback
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate

import pandas as pd
from openpyxl import load_workbook

def make_code_template() -> ChatPromptTemplate:
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
반드시 dataframe에 존재하는 컬럼명을 사용하고 type과 포맷에 맞게 적절한 코드를 작성하세요. 
주어진 DataFrame의 컬럼 별 타입 정보는 다음과 같습니다:
{dftypes}
주어진 DataFrame의 5번째 줄 까지는 다음과 같습니다:
{df}
""" +
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

def make_classify_template() -> ChatPromptTemplate:
    """
    사용자 명령어 리스트를 분석하여,
    1) 연속된 데이터프레임(df) 명령은 하나의 그룹으로 묶어 하나의 JSON 문자열로 'command'에 넣고, 'type'을 'df'로 지정합니다.
    2) '템플릿'(또는 'template') 키워드가 포함된 명령은 'type'을 'excel'로 지정하고, 개별 문자열로 처리합니다.
    출력은 JSON 객체 배열이며, 각 객체는 'command'(문자열)와 'type'('df' 또는 'excel') 필드를 가집니다.

    예시 입력:
      ["압력이 3이상인 것만 필터링 해주세요", "createdAt의 포맷을 YYYY-MM-DD로 바꿔주세요", "KPIreport 템플릿 불러오기"]
    예시 출력:
      [
        {"command":"[\"압력이 3이상인 것만 필터링 해주세요\",\"createdAt의 포맷을 YYYY-MM-DD로 바꿔주세요\"]","type":"df"},
        {"command":"KPIreport 템플릿 불러오기","type":"excel"}
      ]
    """
    # 시스템 메시지: 분류 규칙 정의
    system = SystemMessagePromptTemplate.from_template(
        "당신은 사용자 명령어를 'df'와 'excel'로 분류하는 전문가입니다. "
        "연속된 df 명령은 그룹으로 묶고, 엑셀 파일을 직접 조작해야 하는 '템플릿'(또는 'template')이 포함된 명령은 'excel'로 분류하세요. "
        "각 결과는 'command'(문자열)와 'type'('df' 또는 'excel')을 가진 JSON 객체 배열로 반환해야 합니다."
    )

    # 예시 1: 두 개의 df 연속 → 그룹, excel 단일
    example_h1 = HumanMessagePromptTemplate.from_template(
        '["압력이 3이상인 것만 필터링 해주세요", "createdAt의 포맷을 YYYY-MM-DD로 바꿔주세요", "KPIreport 템플릿 불러오기"]'
    )
    example_a1 = AIMessagePromptTemplate.from_template(
        '[{{"command":"[\\"압력이 3이상인 것만 필터링 해주세요\\",\\"createdAt의 포맷을 YYYY-MM-DD로 바꿔주세요\\"]","type":"df"}},'
        '{{"command":"KPIreport 템플릿 불러오기","type":"excel"}}]'
    )

    # 예시 2: excel 먼저 → 두 개 df 그룹 → excel
    example_h2 = HumanMessagePromptTemplate.from_template(
        '["Report_template 다운로드", "데이터 정렬", "값 범위 필터링", "결과 저장"]'
    )
    example_a2 = AIMessagePromptTemplate.from_template(
        '[{{"command":"Report_template 다운로드","type":"excel"}},'
        '{{"command":"[\\"데이터 정렬\\",\\"값 범위 필터링\\"]","type":"df"}},'
        '{{"command":"결과 저장","type":"excel"}}]'
    )

    # 사용자 입력 바인딩
    user = HumanMessagePromptTemplate.from_template("{cmd_list}")

    # 프롬프트 순서 조합
    return ChatPromptTemplate.from_messages([
        system,
        example_h1, example_a1,
        example_h2, example_a2,
        user
    ])

def make_excel_template() -> ChatPromptTemplate:
    """
    openpyxl을 활용해 기존 .xlsx 파일에 DataFrame을 지정된 위치에 삽입
    - 항상 keep_vba=False
    - few-shot 예시 2개 포함
    """
    return ChatPromptTemplate.from_messages([
        # 시스템 메시지: 역할 명세
        SystemMessagePromptTemplate.from_template(
            "당신은 openpyxl을 사용해 기존 .xlsx 파일을 load → "
            "DataFrame을 지정된 셀 위치에 삽입 → 보존된 서식으로 저장하는 코드 전문가입니다. "
        ),

        # 1번째 페어: 기본 B2 삽입 예시
        HumanMessagePromptTemplate.from_template(
            "템플릿 template.xlsx 의 B2 위치부터 dataframe을 삽입 후 `out1.xlsx` 로 저장:\n"
            "{'Name':['Alice','Bob'], 'Score':[85,92]}"
        ),
        AIMessagePromptTemplate.from_template(
            """```python
from openpyxl import load_workbook

def excel_insert(df, input_path, output_path, start_row=2, start_col=2):
    # 1) 워크북 로드 (keep_vba=False)
    wb = load_workbook(input_path)
    ws = wb.active

    # 2) 헤더 삽입
    for j, col in enumerate(df.columns, start=start_col):
        ws.cell(row=start_row, column=j, value=col)

    # 3) 데이터 삽입
    for i, row in enumerate(df.itertuples(index=False), start=start_row+1):
        for j, val in enumerate(row, start=start_col):
            ws.cell(row=i, column=j, value=val)

    # 4) 저장
    wb.save(output_path)
```"""
        ),

        # 2번째 페어: C5 삽입 예시
        HumanMessagePromptTemplate.from_template(
            "템플릿 report.xlsx 의 C5 위치에 dataFrame을 삽입 후 동일 파일에 덮어쓰기:\n"
            "{'Item':['X','Y','Z'], 'Value':[10,20,30]}"
        ),
        AIMessagePromptTemplate.from_template(
            """```python
from openpyxl import load_workbook

def excel_insert(df, input_path, output_path=None, start_row=5, start_col=3):
    # 1) 워크북 로드 (keep_vba=False)
    wb = load_workbook(input_path)
    ws = wb.active

    # 2) 헤더 삽입
    for j, col in enumerate(df.columns, start=start_col):
        ws.cell(row=start_row, column=j, value=col)

    # 3) 데이터 삽입
    for i, row in enumerate(df.itertuples(index=False), start=start_row+1):
        for j, val in enumerate(row, start=start_col):
            ws.cell(row=i, column=j, value=val)

    # 4) 동일 파일 덮어쓰기
    save_path = output_path or input_path
    wb.save(save_path)
```"""
        ),

        # 실제 사용자 요청
        HumanMessagePromptTemplate.from_template(
            "{input}",
            "{df}"
            )
    ])

def extract_error_info(exc: Exception, code_body: str, stage: str ) -> dict:
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

def insert_df_to_excel(df: pd.DataFrame,
                       input_path: str,
                       output_path: str = None,
                       sheet_name: str = None,
                       start_row: int = 6,
                       start_col: int = 2):
    """
    기존 Excel 파일에 df를 특정 위치에 삽입하고 저장합니다.
    
    Parameters:
    - df: 삽입할 pandas.DataFrame
    - input_path: 원본 엑셀 파일 경로(.xlsx, .xlsm)
    - output_path: 저장할 경로. None이면 input_path에 덮어쓰기
    - sheet_name: None이면 active sheet
    - start_row: 1부터 시작하는 삽입 시작 행 (기본 6)
    - start_col: 1부터 시작하는 삽입 시작 열 (기본 2 → B열)
    """
    # 1) 워크북 로드 (매크로 보존이 필요하면 keep_vba=True)
    wb = load_workbook(filename=input_path, keep_vba=False)
    ws = wb[sheet_name] if sheet_name else wb.active

    # 2) 헤더 삽입
    for j, col_name in enumerate(df.columns, start=start_col):
        ws.cell(row=start_row, column=j, value=col_name)

    # 3) 데이터 삽입
    for i, row in enumerate(df.itertuples(index=False), start=start_row + 1):
        for j, value in enumerate(row, start=start_col):
            ws.cell(row=i, column=j, value=value)

    # 4) 파일 저장
    save_path = output_path or input_path
    wb.save(save_path)
    print(f"Saved to: {save_path}")