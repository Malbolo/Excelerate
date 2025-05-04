
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
    system = SystemMessagePromptTemplate.from_template(
        "사용자가 입력한 커맨드 리스트를 다음 규칙에 따라 그룹화하세요:\n"
        "1) 엑셀 파일 조작 명령(예: '템플릿 불러오기', '데이터 붙여넣기', '파일 저장' 등)은 반드시 개별 요소로 유지합니다.\n"
        "2) 그 외의 단순 명령은 순서를 유지하며, **두 개 이상의 연속된** 단순 명령만 하나의 리스트로 묶습니다.\n"
        "   - 단일 단순 명령은 리스트로 묶지 않고 문자열로 그대로 유지합니다.\n"
        "3) 전체 명령의 순서는 원본 입력과 **완전히 일치**해야 합니다.\n"
        "4) 출력은 순수 JSON array 형태로만 반환하세요."
    )

    # 예시 1: 두 개의 연속된 단순 명령이 있으므로 묶이고, 뒤의 엑셀 조작은 개별
    example_h1 = HumanMessagePromptTemplate.from_template(
        '["압력이 3이상인 것만 필터링 해주세요", "createAt의 포맷을 YYYY-MM-DD로 바꿔주세요", '
        '"KPIreport 템플릿을 불러와 2열에 데이터를 붙여넣어 주세요"]'
    )
    example_a1 = AIMessagePromptTemplate.from_template(
        '[["압력이 3이상인 것만 필터링 해주세요", "createAt의 포맷을 YYYY-MM-DD로 바꿔주세요"], '
        '"KPIreport 템플릿을 불러와 2열에 데이터를 붙여넣어 주세요"]'
    )

    # 예시 2: 단순 명령이 엑셀 조작 명령 사이에 분리되어 있으므로,
    # 각 단일 명령은 그대로 문자열로 남고, 묶이지 않습니다.
    example_h2 = HumanMessagePromptTemplate.from_template(
        '["열 이름 소문자로 변환", "sheet2 템플릿 열기", "그룹별 합계 계산"]'
    )
    example_a2 = AIMessagePromptTemplate.from_template(
        '["열 이름 소문자로 변환", "sheet2 템플릿 열기", "그룹별 합계 계산"]'
    )

    user = HumanMessagePromptTemplate.from_template(
        "사용자 입력: {cmd_list}"
    )

    prompt = ChatPromptTemplate.from_messages([
        system,
        example_h1, example_a1,
        example_h2, example_a2,
        user,
    ])
    return prompt

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