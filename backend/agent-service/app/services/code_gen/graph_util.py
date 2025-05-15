
import re
import traceback
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from difflib import SequenceMatcher
from typing import Optional
import pandas as pd
from openpyxl import load_workbook

## 추 후 다양한 기능을(단순 불러오기, dataframe 치환, 다중 저장 등) 수행시키고 싶다면 해당 템플릿을 사용해 엑셀 코드를 생성하도록 수정해야 할 것
def make_excel_template() -> ChatPromptTemplate:
    """
    openpyxl을 활용해 기존 .xlsx 파일에 DataFrame을 지정된 위치에 삽입
    - 항상 keep_vba=False
    - few-shot 예시 2개 포함
    insert_df_to_excel에 해당 코드 포함되어 있음
    불러와 바로 실행 가능한 코드로 생성성
    """
    return ChatPromptTemplate.from_messages([
        # 시스템 메시지: 역할 명세
        SystemMessagePromptTemplate.from_template(
            "당신은 openpyxl을 사용해 기존 .xlsx 파일을 load → "
            "DataFrame을 지정된 셀 위치에 삽입 → 보존된 서식으로 저장하는 코드 전문가입니다. "
        ),

        # 1번째 페어: 기본 B2 삽입 예시
        HumanMessagePromptTemplate.from_template(
            "템플릿 EOE 의 B2 위치부터 dataframe을 삽입 후 out1으로 저장:\n"
            "{'Name':['Alice','Bob'], 'Score':[85,92]}"
        ),
        AIMessagePromptTemplate.from_template(
            """
from tempfile import TemporaryDirectory
import os
import pandas as pd
from app.services.code_gen.graph_util import insert_df_to_excel
from app.utils.minio_client import MinioClient

# 테스트 템플릿에 처리된 dataframe 붙여넣기
minio = MinioClient()
with TemporaryDirectory() as workdir:
    tpl = os.path.join(workdir, "report.xlsx")
    out = os.path.join(workdir, "report_result.xlsx")
    # 다운로드
    minio.download_template("EOE", tpl)
    # 삽입
    insert_df_to_excel(df, tpl, out,
                    sheet_name=None,
                    start_row=2,
                    start_col=2)
    # 업로드
    minio.upload_result("auto", "out1", out)
"""
        ),

        # 2번째 페어: C5 삽입 예시
        HumanMessagePromptTemplate.from_template(
            "템플릿 report.xlsx 의 C5 위치에 dataFrame을 삽입 후 동일 파일에 덮어쓰기:\n"
            "{'Item':['X','Y','Z'], 'Value':[10,20,30]}"
        ),
        AIMessagePromptTemplate.from_template(
            """
from tempfile import TemporaryDirectory
import os
import pandas as pd
from app.services.code_gen.graph_util import insert_df_to_excel
from app.utils.minio_client import MinioClient

# 테스트 템플릿에 처리된 dataframe 붙여넣기
minio = MinioClient()
with TemporaryDirectory() as workdir:
    tpl = os.path.join(workdir, "report.xlsx")
    out = os.path.join(workdir, "report_result.xlsx")
    # 다운로드
    minio.download_template("report.xlsx", tpl)
    # 삽입
    insert_df_to_excel(df, tpl, out,
                    sheet_name=None,
                    start_row=5,
                    start_col=3)
    # 업로드
    minio.upload_result("auto", "report.xlsx", out)
"""
        ),

        # 실제 사용자 요청
        HumanMessagePromptTemplate.from_template(
            "{input}",
            "{df}"
            )
    ])

def extract_error_info(exc: Exception, code_body: str, stage: str, commands: list[str], similarity_threshold: float = 0.5) -> dict:
    """
    Exception과 원본 코드 문자열, 실패 단계를 받아서
    빈 줄을 블록 구분자로 사용해, 해당 블록 시작(가장 가까운 빈 줄 이후)부터
    에러 라인까지의 snippet과, 블록 시작 주석을 command로 추출합니다.
    그 command가 commands 내에서 얼마나 유사한지 보고, similarity_threshold 이상이면 그 인덱스
    를 반환합니다.
    """
    # 1) traceback에서 마지막 프레임 정보 추출
    tb_last = traceback.extract_tb(exc.__traceback__)[-1]
    raw_lineno = tb_last.lineno

    # 2) 코드 본문을 줄 단위로 분리
    lines = code_body.splitlines()
    total = len(lines)

    # 3) 1-based lineno → 0-based index로 변환, 범위 clamp
    err_idx = min(raw_lineno - 1, total - 1)

    # 4) 블록 시작 찾기: err_idx 바로 위부터 검색해 최초의 빈 줄 이후를 블록 시작으로
    block_start: int = 0
    for idx in range(err_idx, -1, -1):
        line_strip = lines[idx].lstrip()
        # (1) 주석으로 시작하고, (2) 바로 위가 빈 줄이거나 맨 앞이면 블록 시작
        if line_strip.startswith("#") and (idx == 0 or lines[idx-1].strip() == ""):
            block_start = idx
            break

    # 5) 블록 시작 줄(주석)에서 command 추출
    #    예: "# defect_rate가 1 이상인 데이터만 필터링 해주세요."
    raw_comment = lines[block_start].lstrip()
    command = raw_comment[1:].strip() if raw_comment.startswith("#") else ""
    
    # 6) command_index 찾기
    best_idx   : Optional[int]   = None
    best_ratio : float = 0.0
    for idx, cand in enumerate(commands):
        # SequenceMatcher.ratio()는 0~1 사이 값을 반환
        ratio = SequenceMatcher(None, command, cand).ratio()
        if ratio > best_ratio:
            best_ratio, best_idx = ratio, idx

    if best_ratio >= similarity_threshold:
        command_index = best_idx
    else:
        command_index = None

    # 7) snippet 생성 (block_start 부터 err_idx 까지)
    snippet_lines = []
    for i in range(block_start, err_idx + 1):
        text = lines[i].rstrip()
        prefix = "→" if i == err_idx else "  "
        snippet_lines.append(f"{prefix} {i+1:4d}: {text}")
    snippet = "\n".join(snippet_lines)

    return {
        "error_msg": {
            "stage":    stage,
            "message":  str(exc),
            "file":     tb_last.filename,
            "line":     raw_lineno,
            "command":  command,
            "command_index": command_index,
            "code":     snippet,
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
    """
    sheet_repr = repr(sheet_name) if sheet_name is not None else 'None'
    return f"""
# Excel 작업 시작
# {template_name} 템플릿의 {start_col}열 {start_row}행에 dataframe 붙여넣기
workdir = mkdtemp()
tpl    = os.path.join(workdir, "{template_name}.xlsx")
out    = os.path.join(workdir, "{output_name}.xlsx")

# 다운로드
minio = MinioClient()
minio.download_template("{template_name}", tpl)

# 삽입
insert_df_to_excel(
    df, tpl, out,
    sheet_name={sheet_repr},
    start_row={start_row},
    start_col={start_col},
)

# 업로드
minio.upload_result("{user_id}", "{template_name}", out)
# Excel 작업 끝
"""