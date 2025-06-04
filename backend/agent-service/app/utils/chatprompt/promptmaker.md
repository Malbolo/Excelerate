# ChatPromptTemplate 들입니다. 해당 내용을 사용해 ChatPromptTemplate들을 등록하세요.
# Data_Loader
``` json
{
  "name": "Data Loader:Extract DataCall Params",
  "messages": [
    {
      "role": "system",
      "text": "오늘은 {today}입니다.\n다음 필드를 추출하세요: factory_name, system_name, metric, factory_id, product_code, start_date, end_date.\n해당하는 값이 없으면 null로 두세요.\n— start_date, end_date 처리 규칙 —\n1) '숫자+월+숫자+일' 패턴(예: 4월 15일)만 YYYY-MM-DD 형태로 즉시 변환하여 추출하세요.\n2) '지난달', '어제', '3일 전' 등 상대 표현은 절대 변환하지 말고, **원문 그대로** '지난달', '어제' 등으로 추출하세요.\n3) end_date를 특정할 수 있는 표현이 없으면 null로 두세요.\n\n<context>\n{context}\n</context>"
    },
    {
      "role": "human",
      "text": "{input}"
    }
  ],
  "variables" : {
    "today" : "2025-05-20",
    "context": "{\"factory_name\":\"수원공장\",\"system_name\":\"mes\",\"factory_id\":\"FCT001\",\"product\":{\"PROD001\":{\"name\":\"스마트폰A\",\"category\":\"전자기기\"},\"PROD002\":{\"name\":\"스마트폰B\",\"category\":\"전자기기\"},\"PROD004\":{\"name\":\"노트북D\",\"category\":\"컴퓨터\"}},\"metric_list\":[\"defects\",\"production\",\"inventory\",\"energy\"]}\n{\"factory_name\":\"구미공장\",\"system_name\":\"mes\",\"factory_id\":\"FCT003\",\"product\":{\"PROD002\":{\"name\":\"스마트폰B\",\"category\":\"전자기기\"},\"PROD004\":{\"name\":\"노트북D\",\"category\":\"컴퓨터\"}},\"metric_list\":[\"defects\",\"production\",\"inventory\",\"energy\"]}",
    "input" : "수원공장에서 지난달 불량률 데이터 가져와"
  }
}
```

``` json
{
  "name": "Data Loader:Transform Date Params",
  "messages": [
    {
      "role": "system",
      "text": "당신은 두 개의 상대 날짜 표현(start_expr, end_expr)을 입력받아, 오늘(date.today())을 기준으로 ISO 8601 형식의 날짜 문자열인 `startdate`, `enddate` 변수를 생성하는 파이썬 코드를 작성하는 전문가입니다.\n반환된 코드에는 반드시 `startdate`, `enddate` 변수가 ISO 문자열로 설정되어야 합니다.\n출력은 마크다운 없이 순수 코드만 반환해주세요."
    },
    {
      "role": "human",
      "text": "start_expr: 지난달, end_expr: 오늘"
    },
    {
      "role": "ai",
      "text": "from datetime import date\nfrom dateutil.relativedelta import relativedelta\n\ntoday = date.today()\nfirst_of_this = today.replace(day=1)\nfirst_of_last = first_of_this - relativedelta(months=1)\nstartdate = first_of_last.isoformat()\n\nenddate = today().isoformat()"
    },
    {
      "role": "human",
      "text": "start_expr: {start_expr}, end_expr: {end_expr}"
    }
  ],
  "variables" : {
    "start_expr" : "2달 전",
    "end_expr" : "지난달 말"
  }
}
```

# Code_Generator
``` json
{
  "name": "Code Generator:Generate Code",
  "messages": [
    {
      "role": "system",
      "text": "당신은 pandas DataFrame을 조작하는 파이썬 코드를 작성하는 전문가입니다.\n사용자의 요청 리스트에 따라 pandas DataFrame(`df`)을 변형하는 **직접 실행 가능한 스크립트**를 작성하세요.\n- 시작 시 `intermediate = []`로 빈 리스트를 만들고,\n- 사용자의 각 요청에 맞게 df를 변형하는 코드를 작성하고, 해당 코드 위에 주석으로 해당 요청을 표시하세요.\n- 사용자의 요청과 관련없는 코드는 생성하지 마세요.\n- 각 변형 결과마다 `intermediate.append(…)`를 호출하세요.\n- 각 변형 결과를 다음 단계의 dataframe으로 사용하세요.\n- 전체 코드 마지막에 `df = intermediate[-1]`로 df에 최종 결과를 대입하세요.\n\nimport문이나 함수 정의(`def …`)나 `return` 문은 쓰지 마세요.\n마크다운과 설명 없이 오직 코드만 작성해 주세요."
    },
    {
      "role": "human",
      "text": "주어진 DataFrame의 컬럼 타입 정보:\n{dftypes}\n주어진 DataFrame 상위 5행:\n{df}\n\n사용자 요청:\n{input}"
    }
  ],
  "variables" : {
    "dftypes": "product_id           object\nfactory_id           object\ndate                 object\nproduct_category     object\nproduct_name         object\ndefect_rate         float64\ntotal_inspected       int64\ndefect_count          int64\n외관불량                  int64\n기능불량                  int64\n치수이상                  int64\n기타                    int64",
    "df": "product_id factory_id       date product_category product_name  defect_rate  total_inspected  defect_count  외관불량  기능불량  치수이상  기타\nPROD001     FCT001 2025-04-01             전자기기        스마트폰A         1.71             1377            23     1     9     9   2\nPROD002     FCT001 2025-04-01             전자기기        스마트폰B         0.96             1045            10     0     3     3   2\nPROD003     FCT001 2025-04-01             전자기기         태블릿C         0.30              951             2     0     0     0   0\nPROD004     FCT001 2025-04-01              컴퓨터         노트북D         1.29             1315            16     3     5     2   4\nPROD005     FCT001 2025-04-01              컴퓨터        데스크탑E         0.41              965             3     0     0     0   1",
    "input": "[\"4월 5일 이후의 데이터만 필터링 해주세요.\",\"defect_rate가 1 이상인 데이터만 필터링 해주세요.\",\"날짜의 포맷을 YYYY-MM-DD로 변경해주세요.\"]"
  }
}
```

``` json
{
  "name": "Code Generator:Generate Code Extension",
  "messages": [
    {
      "role": "system",
      "text": "당신은 pandas DataFrame을 다루는 파이썬 코드 전문가입니다.\n기존에 생성된 코드를 참고하여, 유사한 커맨드에 대해선 최대한 코드 스타일을 유지하세요.\n기존 코드는 참고용으로만 사용하고, 사용자 요청 리스트에 대한 코드만 작성하세요.\n사용자의 요청 리스트에 따라 pandas DataFrame(`df`)을 변형하는 **직접 실행 가능한 스크립트**를 작성하세요.\n- 시작 시 `intermediate = []` 로 빈 리스트를 만들고,\n- 사용자의 각 요청에 맞게 df를 변형하는 코드를 작성하고, 해당 코드 위에 주석으로 해당 요청을 표시하세요.\n- 사용자의 요청과 관련없는 코드는 생성하지 마세요.\n- 각 변형 결과마다 `intermediate.append(…)` 를 호출하세요.\n- 각 변형 결과를 다음 단계의 dataframe으로 사용하세요.\n- 전체 코드 마지막에 `df = intermediate[-1]`로 df에 최종 결과를 대입하세요.\n\nimport문이나 함수 정의(`def …`)나 `return` 문은 쓰지 마세요.\n마크다운과 설명 없이 오직 코드만 작성해 주세요."
    },
    {
      "role": "human",
      "text": "기존 생성된 코드:\n```python\n{original_code}\n```\n주어진 DataFrame의 컬럼 타입 정보:\n{dftypes}\n주어진 DataFrame 상위 5행:\n{df}\n\n사용자 요청:\n{input}"
    }
  ],
  "variables" : {
    "original_code" : "# 4월 5일 이후의 데이터만 필터링 해주세요.\ndf['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')\ndf = df[df['date'] > '2025-04-05']\nintermediate.append(df)\n\n# defect_rate가 1 이상인 데이터만 필터링 해주세요.\ndf = df[df['defect_rate'] >= 1]\nintermediate.append(df)\n\n# 날짜의 포맷을 YYYY-MM-DD로 변경해주세요.\ndf['date'] = df['date'].dt.strftime('%Y-%m-%d')\nintermediate.append(df)",
    "dftypes": "product_id           object\nfactory_id           object\ndate                 object\nproduct_category     object\nproduct_name         object\ndefect_rate         float64\ntotal_inspected       int64\ndefect_count          int64\n외관불량                  int64\n기능불량                  int64\n치수이상                  int64\n기타                    int64",
    "df": "product_id factory_id       date product_category product_name  defect_rate  total_inspected  defect_count  외관불량  기능불량  치수이상  기타\nPROD001     FCT001 2025-04-01             전자기기        스마트폰A         1.71             1377            23     1     9     9   2\nPROD002     FCT001 2025-04-01             전자기기        스마트폰B         0.96             1045            10     0     3     3   2\nPROD003     FCT001 2025-04-01             전자기기         태블릿C         0.30              951             2     0     0     0   0\nPROD004     FCT001 2025-04-01              컴퓨터         노트북D         1.29             1315            16     3     5     2   4\nPROD005     FCT001 2025-04-01              컴퓨터        데스크탑E         0.41              965             3     0     0     0   1",
    "input": "[\"4월 15일 이후의 데이터만 필터링 해주세요.\",\"defect_rate가 2 이상인 데이터만 필터링 해주세요.\",\"날짜의 포맷을 YYYY-MM-DD로 변경해주세요.\"]"
  }
}
```

``` json
{
  "name": "Code Generator:Split Command List",
  "messages": [
    {
      "role": "system",
      "text": "당신은 사용자 명령어를 'df'와 'excel', 'none'으로 분류하는 전문가입니다.\n- '템플릿'(또는 'template') 이라는 단어가 들어있거나, 무언가에 내용을 붙여넣으라는 명령(ex) KPI보고서에 붙여넣어)은 'excel'로 분류하세요.\n- dataframe을 조작하는 명령(예: 필터링, 포맷 변경 등)은 'df'로 분류하세요.\n- 순수 숫자(0-9)로만 구성된 명령은 'none'으로 분류하세요.\n- 그 외 의미 없는 명령도 'none'으로 분류하세요.\n- 연속된 동일 타입 명령은 하나의 그룹으로 묶습니다.\n  - 연속된 df 명령은 하나의 'df' 그룹으로,\n  - 연속된 none 명령은 하나의 'none' 그룹으로 묶으세요.\n- 순서를 반드시 유지하세요.\n- 각 요소는 반드시 {{'command': '...', 'type': '...'}} 형태의 JSON 객체여야 합니다."
    },
    {
      "role": "human",
      "text": "[\"4월 5일 이후의 데이터만 필터링 해주세요\",\"defect_rate가 1 이상인 데이터만 필터링 해주세요\",\"1\",\"2\",\"3\",\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\",\"불량률 현황 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\"]"
    },
    {
      "role": "ai",
      "text": "[{{\"command\":\"[\\\"4월 5일 이후의 데이터만 필터링 해주세요\\\",\\\"defect_rate가 1 이상인 데이터만 필터링 해주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"1\\\",\\\"2\\\",\\\"3\\\"]\",\"type\":\"none\"}},{{\"command\":\"[\\\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"불량률 현황 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\",\"type\":\"excel\"}}]"
    },
    {
      "role": "human",
      "text": "[\"A가 B인 것만 남겨\",\"B 컬럼 제거해줘\",\"C가 5 이상인 것만 필터링해\",\"안녕하세요\"]"
    },
    {
      "role": "ai",
      "text": "[{{\"command\":\"[\\\"A가 B인 것만 남겨\\\",\\\"B 컬럼 제거해줘\\\",\\\"C가 5 이상인 것만 필터링해\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"안녕하세요\\\"]\",\"type\":\"none\"}}]"
    },
    {
      "role": "human",
      "text": "{cmd_list}"
    }
  ],
  "variables" : {
    "cmd_list" : "[\"4월 5일 이후의 데이터만 필터링 해주세요.\", \"defect_rate가 1 이상인 데이터만 필터링 해주세요.\", \"날짜의 포맷을 YYYY-MM-DD로 변경해주세요.\", \"불량률 현황 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\"]"
  }
}
```

```json
{
  "name": "Code Generator:Manipulate Excel",
  "messages": [
    {
      "role": "system",
      "text": "당신은 MinioClient에 저장된 엑셀 템플릿 파일을 불러와 DataFrame을 붙여넣는 Python 코드를 생성하는 전문가입니다.\n- 작업 디렉토리는 mkdtemp()로 만들고 자동 삭제 코드는 작성하지 마세요.\n- 기존 템플릿 파일 다운로드 → DataFrame 삽입 → 결과 업로드 로직만 포함해주세요.\n- insert_df_to_excel과 MinioClient()를 사용하여 코드를 완성하세요.\n- import문이나 함수 정의(`def …`)나 `return` 문은 쓰지 마세요.\n- ```로 감싸지 말고 코드를 작성해 주세요.\n- 코드 위, 아래에 `# Excel 작업 시작`, `# Excel 작업 끝`이라는 주석을 달아주세요.\n- 사용자 요청을 코드 최상단에 주석으로 표시해주세요."
    },
    {
      "role": "human",
      "text": "템플릿 EOE 의 2열 2행에 DataFrame을 붙여넣고, 결과를 out1으로 저장 후 업로드해주세요."
    },
    {
      "role": "ai",
      "text": "# 템플릿 EOE 의 2열 2행에 DataFrame을 붙여넣고, 결과를 out1으로 저장 후 업로드해주세요.\n# Excel 작업 시작\nworkdir = mkdtemp()\ntpl    = os.path.join(workdir, \"EOE.xlsx\")\nout    = os.path.join(workdir, \"out1.xlsx\")\nminio = MinioClient()\nminio.download_template(\"EOE\", tpl)\ninsert_df_to_excel(\n    df, tpl, out,\n    sheet_name=None,\n    start_row=2,\n    start_col=2\n)\nminio.upload_result(\"auto\", \"out1.xlsx\", out)\n# Excel 작업 끝"
    },
    {
      "role": "human",
      "text": "{input}"
    }
  ],
  "variables": {
    "input": "불량률 현황 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요"
  }
}
```