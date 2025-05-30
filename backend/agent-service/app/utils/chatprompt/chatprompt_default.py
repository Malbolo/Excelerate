# 챗프롬프트 기본 값 모음 (프롬프트 등록 안해도 기본 동작 하도록 설정)
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate

# Data Loader:Extract DataCall Params
def extract_datacall_params_prompt() -> ChatPromptTemplate:
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

# Data Loader:Transform Date Params
def transform_date_params_template() -> ChatPromptTemplate:
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

# Code Generator:Manipulate Excel 기본 프롬프트
def manipulate_excel_template() -> ChatPromptTemplate:
    """
    Airflow DAG Task에서 실행할 수 있는 엑셀 코드 스니펫을 생성하는 Prompt
    - 작업 디렉토리는 mkdtemp()로 생성
    - 자동 삭제 로직은 포함하지 않음 (downstream Task에서 처리)
    - 다운로드, DataFrame 삽입, 업로드만 수행
    - few-shot 예시 1개 포함
    """
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """
당신은 MinioClient에 저장된 엑셀 템플릿 파일을 불러와 DataFrame을 붙여넣는 Python 코드를 생성하는 전문가입니다.
- 작업 디렉토리는 mkdtemp()로 만들고 자동 삭제 코드는 작성하지 마세요.
- 기존 템플릿 파일 다운로드 → DataFrame 삽입 → 결과 업로드 로직만 포함해주세요.
- insert_df_to_excel과 MinioClient()를 사용하여 코드를 완성하세요.
- import문이나 함수 정의(`def …`)나 `return` 문은 쓰지 마세요.
- ```로 감싸지 말고 코드를 작성해 주세요.
- 코드 위, 아래에 `# Excel 작업 시작`, `# Excel 작업 끝`이라는 주석을 달아주세요.
- 사용자 요청을 코드 최상단에 주석으로 표시해주세요.
"""
        ),
        HumanMessagePromptTemplate.from_template(
            """
템플릿 EOE 의 2열 2행에 DataFrame을 붙여넣고, 결과를 out1으로 저장 후 업로드해주세요.
"""
        ),
        AIMessagePromptTemplate.from_template(
            """
# Excel 작업 시작
workdir = mkdtemp()
tpl    = os.path.join(workdir, "EOE.xlsx")
out    = os.path.join(workdir, "out1.xlsx")

# 다운로드
minio = MinioClient()
minio.download_template("EOE", tpl)

# 삽입
insert_df_to_excel(
    df, tpl, out,
    sheet_name=None,
    start_row=2,
    start_col=2,
)

# 업로드
minio.upload_result("auto", "out1.xlsx", out)
# Excel 작업 끝
"""
        ),
        # 실제 사용자 요청
        HumanMessagePromptTemplate.from_template(
            "{input}"
        ),
    ])

# Code Generator:Generate Code
def generate_code_template() -> ChatPromptTemplate:
    # 2) 시스템 메시지: df와 파라미터를 받아 필터링 코드를 생성한다는 역할 정의
    system_template = SystemMessagePromptTemplate.from_template(
        "당신은 pandas DataFrame을 조작하는 파이썬 코드를 작성하는 전문가입니다.\n사용자의 요청 리스트에 따라 pandas DataFrame(`df`)을 변형하는 **직접 실행 가능한 스크립트**를 작성하세요.\n- 시작 시 `intermediate = []`로 빈 리스트를 만들고,\n- 사용자의 각 요청에 맞게 df를 변형하는 코드를 작성하고, 해당 코드 위에 주석으로 해당 요청을 표시하세요.\n- 사용자의 요청과 관련없는 코드는 생성하지 마세요.\n- 각 변형 결과마다 `intermediate.append(…)`를 호출하세요.\n- 각 변형 결과를 다음 단계의 dataframe으로 사용하세요.\n- 전체 코드 마지막에 `df = intermediate[-1]`로 df에 최종 결과를 대입하세요.\n\nimport문이나 함수 정의(`def …`)나 `return` 문은 쓰지 마세요.\n마크다운과 설명 없이 오직 코드만 작성해 주세요."
    )

    # 3) 휴먼 메시지: start_date, end_date 변수를 받아 df 필터링 함수 코드를 만들어 달라는 요청
    human_template = HumanMessagePromptTemplate.from_template(
        """
주어진 DataFrame의 컬럼 타입 정보:\n{dftypes}\n주어진 DataFrame 상위 5행:\n{df}\n\n사용자 요청:\n{input}
"""
    )

    # 4) 두 메시지를 합쳐 PromptTemplate 생성
    prompt = ChatPromptTemplate.from_messages([system_template, human_template])
    return prompt

# Code Generator:Generate Code Extension
def generate_code_extension_template() -> ChatPromptTemplate:
    system = SystemMessagePromptTemplate.from_template(
        "당신은 pandas DataFrame을 다루는 파이썬 코드 전문가입니다.\n기존에 생성된 코드를 참고하여, 유사한 커맨드에 대해선 최대한 코드 스타일을 유지하세요.\n기존 코드는 참고용으로만 사용하고, 사용자 요청 리스트에 대한 코드만 작성하세요.\n사용자의 요청 리스트에 따라 pandas DataFrame(`df`)을 변형하는 **직접 실행 가능한 스크립트**를 작성하세요.\n- 시작 시 `intermediate = []` 로 빈 리스트를 만들고,\n- 사용자의 각 요청에 맞게 df를 변형하는 코드를 작성하고, 해당 코드 위에 주석으로 해당 요청을 표시하세요.\n- 사용자의 요청과 관련없는 코드는 생성하지 마세요.\n- 각 변형 결과마다 `intermediate.append(…)` 를 호출하세요.\n- 각 변형 결과를 다음 단계의 dataframe으로 사용하세요.\n- 전체 코드 마지막에 `df = intermediate[-1]`로 df에 최종 결과를 대입하세요.\n\nimport문이나 함수 정의(`def …`)나 `return` 문은 쓰지 마세요.\n마크다운과 설명 없이 오직 코드만 작성해 주세요."
    )
    human = HumanMessagePromptTemplate.from_template(
        "기존 생성된 코드:\n```python\n{original_code}\n```\n주어진 DataFrame의 컬럼 타입 정보:\n{dftypes}\n주어진 DataFrame 상위 5행:\n{df}\n\n사용자 요청:\n{input}"
    )
    return ChatPromptTemplate.from_messages([system, human])

# Code Generator:Split Command List
def split_command_list_template() -> ChatPromptTemplate:
    """
    사용자 명령어 리스트를 분석하여,
    1) 연속된 데이터프레임(df) 명령은 하나의 그룹으로 묶어 하나의 JSON 문자열로 'command'에 넣고, 'type'을 'df'로 지정합니다.
    2) '템플릿'(또는 'template') 키워드가 포함된 명령은 'type'을 'excel'로 지정하고, 개별 문자열로 처리합니다.
    3) 아무 의미없는 명령은 'type'을 'none'으로 지정하고 무시합니다.
    출력은 JSON 객체 배열이며, 각 객체는 'command'(문자열)와 'type'('df' 또는 'excel' 또는 'none') 필드를 가집니다.

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
    """
당신은 사용자 명령어를 'df'와 'excel', 'none'으로 분류하는 전문가입니다.
- '템플릿' 또는 'template'이라는 단어가 들어있는 명령만 'excel'로 분류하세요.
- dataframe을 조작하는 명령(예: 필터링, 포맷 변경 등)은 'df'로 분류하세요.
- 순수 숫자(0-9)로만 구성된 명령은 'none'으로 분류하세요.
- 그 외 의미 없는 명령도 'none'으로 분류하세요.
- 연속된 동일 타입 명령은 하나의 그룹으로 묶습니다.
  - 연속된 df 명령은 하나의 'df' 그룹으로,
  - 연속된 none 명령은 하나의 'none' 그룹으로 묶으세요.
- 순서를 반드시 유지하세요.
- 각 요소는 반드시 {{'command': '...', 'type': '...'}} 형태의 JSON 객체여야 합니다.
"""
)

    # 그룹화 예시
    example_h1 = HumanMessagePromptTemplate.from_template(
        '["4월 5일 이후의 데이터만 필터링 해주세요",'
        '"defect_rate가 1 이상인 데이터만 필터링 해주세요",'
        '"1","2","3",'
        '"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요",'
        '"테스트 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요"]'
    )
    example_a1 = AIMessagePromptTemplate.from_template(
        '['
          '{{"command":"[\\"4월 5일 이후의 데이터만 필터링 해주세요\\",'
                         '\\"defect_rate가 1 이상인 데이터만 필터링 해주세요\\"]","type":"df"}},'
          '{{"command":"[\\"1\\",\\"2\\",\\"3\\"]","type":"none"}},'
          '{{"command":"[\\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\\"]","type":"df"}},'
          '{{"command":"테스트 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요","type":"excel"}}'
        ']'
    )

    # 예시 2: excel 먼저 → 두 개 df 그룹 → excel
    example_h2 = HumanMessagePromptTemplate.from_template(
        '["A가 B인 것만 남겨", "B 컬럼 제거해줘", "C가 5 이상인 것만 필터링해", "집가고 싶다"]'
    )
    example_a2 = AIMessagePromptTemplate.from_template(
        '[{{"command":"[\\"A가 B인 것만 남겨\\",\\"B 컬럼 제거해줘\\",\\"C가 5 이상인 것만 필터링해\\"]","type":"df"}},'
        '{{"command":"[\\"집가고 싶다\\"]","type":"none"}}]'
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

