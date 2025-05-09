
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
사용자의 요청에 따라 pandas DataFrame(`df`)을 단계별로 변형하는 **직접 실행 가능한 스크립트**를 작성하세요.
- 시작 시 `intermediate = []` 로 빈 리스트를 만들고,
- 각 변형 결과마다 `intermediate.append(…)` 를 호출하세요.
- 각 변형 결과를 다음 단계의 dataframe으로 사용하세요

함수 정의(`def …`)나 `return` 문은 쓰지 마세요.

주어진 DataFrame의 컬럼 타입 정보:
{dftypes}
주어진 DataFrame 상위 5행:
{df}

설명 없이 오직 코드만 작성해 주세요.

사용자 요청:
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

def make_extract_excel_params_template() -> ChatPromptTemplate:
    system = SystemMessagePromptTemplate.from_template(
        "사용자 명령어에서 엑셀 템플릿 이름, 시트 이름(선택), 삽입 시작 위치, 결과 파일명을"
        " JSON으로 추출해 주세요."
    )
    example_h = HumanMessagePromptTemplate.from_template(
        "\"KPIreport 템플릿을 불러와서 3열 4행부터 데이터를 꽉 차게 삽입한 뒤 KPI_결과.xlsx로 저장해줘\""
    )
    example_a = AIMessagePromptTemplate.from_template(
        "{{\n"
        "  \"template_name\": \"KPIreport\",\n"
        "  \"sheet_name\": null,\n"
        "  \"start_row\": 4,\n"
        "  \"start_col\": 3,\n"
        "  \"output_name\": \"KPI_결과.xlsx\"\n"
        "}}"
    )
    user = HumanMessagePromptTemplate.from_template("{command}")
    return ChatPromptTemplate.from_messages([system, example_h, example_a, user])

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

    # 병합 셀 범위 리스트
    merged_ranges = list(ws.merged_cells.ranges)

    # 2) 헤더 삽입
    for j, col_name in enumerate(df.columns, start=start_col):
        ws.cell(row=start_row, column=j, value=col_name)

    # 3) 데이터 삽입
    for i, row in enumerate(df.itertuples(index=False), start=start_row + 1):
        for j, value in enumerate(row, start=start_col):
            # 병합 셀 내 포함 여부 확인: numeric bounds 검사
            target = None
            for merged in merged_ranges:
                if merged.min_row <= i <= merged.max_row and merged.min_col <= j <= merged.max_col:
                    target = (merged.min_row, merged.min_col)
                    break
            if target:
                ws.cell(row=target[0], column=target[1], value=value)
            else:
                ws.cell(row=i, column=j, value=value)

    # 4) 파일 저장
    save_path = output_path or input_path
    wb.save(save_path)
    print(f"Saved to: {save_path}")

def make_excel_code_snippet(template_name: str,
                             output_name: str,
                             start_row: int,
                             start_col: int,
                             sheet_name: str = None,
                             user_id: str = "test") -> str:
    """
    Excel 작업을 Airflow 등에서 재실행할 수 있도록 하는 Python 코드 스니펫을 생성합니다.
    airflow와 연결 시, insert_df_to_excel과 MinioClient를 연결할 필요가 있습니다.(주입해도 되고)
    """
    sheet_repr = repr(sheet_name) if sheet_name is not None else 'None'
    return f"""
from tempfile import TemporaryDirectory
import os
import pandas as pd
from app.services.code_gen.graph_util import insert_df_to_excel
from app.utils.minio_client import MinioClient

# {template_name} 템플릿에 처리된 dataframe 붙여넣기
minio = MinioClient()
with TemporaryDirectory() as workdir:
    tpl = os.path.join(workdir, "{template_name}.xlsx")
    out = os.path.join(workdir, "{output_name}")
    # 다운로드
    minio.download_template("{template_name}", tpl)
    # 삽입
    insert_df_to_excel(df, tpl, out,
                    sheet_name={sheet_repr},
                    start_row={start_row},
                    start_col={start_col})
    # 업로드
    minio.upload_result("{user_id}", "{template_name}", out)
"""
