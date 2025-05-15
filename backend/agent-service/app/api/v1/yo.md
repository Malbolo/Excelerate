자 응답 형식을 한번 싹 고칠거야. 지금 응답은 이런 식이거든?
``` json
{
  "result": "success",
  "data": {
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
    ]
  }
}
```

messages를 보면 [{role, text}] 형태잖아? 이렇게 말고 다음과 같이 응답이 가도록 하고 싶어.
``` json
      {
        "system": "당신은 pandas DataFrame을 조작하는 파이썬 코드를 작성하는 전문가입니다.\n사용자의 요청 리스트에 따라 pandas DataFrame(`df`)을 변형하는 **직접 실행 가능한 스크립트**를 작성하세요.\n- 시작 시 `intermediate = []`로 빈 리스트를 만들고,\n- 사용자의 각 요청에 맞게 df를 변형하는 코드를 작성하고, 해당 코드 위에 주석으로 해당 요청을 표시하세요.\n- 사용자의 요청과 관련없는 코드는 생성하지 마세요.\n- 각 변형 결과마다 `intermediate.append(…)`를 호출하세요.\n- 각 변형 결과를 다음 단계의 dataframe으로 사용하세요.\n- 전체 코드 마지막에 `df = intermediate[-1]`로 df에 최종 결과를 대입하세요.\n\nimport문이나 함수 정의(`def …`)나 `return` 문은 쓰지 마세요.\n마크다운과 설명 없이 오직 코드만 작성해 주세요.",

        "human": "주어진 DataFrame의 컬럼 타입 정보:\n{dftypes}\n주어진 DataFrame 상위 5행:\n{df}\n\n사용자 요청:\n{input}" 
      }
```

차이를 알겠지? role과 text 키가 있는 dict의 리스트가 아니라 json에 role이 key고 text가 value로 들어가는 거야.

여기에 추가로 system과 human 사이의 human, ai 응답쌍이 있으면 그건 fewshot키의 배열로 담기게 하고 싶어. 예를들어
``` json
  [ 
      {
        "role": "system",
        "text": "당신은 사용자 명령어를 'df'와 'excel', 'none'으로 분류하는 전문가입니다.\n- '템플릿' 또는 'template'이라는 단어가 들어있는 명령만 'excel'로 분류하세요.\n- dataframe을 조작하는 명령(예: 필터링, 포맷 변경 등)은 'df'로 분류하세요.\n- 순수 숫자(0-9)로만 구성된 명령은 'none'으로 분류하세요.\n- 그 외 의미 없는 명령도 'none'으로 분류하세요.\n- 연속된 동일 타입 명령은 하나의 그룹으로 묶습니다.\n  - 연속된 df 명령은 하나의 'df' 그룹으로,\n  - 연속된 none 명령은 하나의 'none' 그룹으로 묶으세요.\n- 순서를 반드시 유지하세요.\n- 각 요소는 반드시 {{'command': '...', 'type': '...'}} 형태의 JSON 객체여야 합니다."
      },
      {
        "role": "human",
        "text": "[\"4월 5일 이후의 데이터만 필터링 해주세요\",\"defect_rate가 1 이상인 데이터만 필터링 해주세요\",\"1\",\"2\",\"3\",\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\",\"테스트 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\"]"
      },
      {
        "role": "ai",
        "text": "[{{\"command\":\"[\\\"4월 5일 이후의 데이터만 필터링 해주세요\\\",\\\"defect_rate가 1 이상인 데이터만 필터링 해주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"1\\\",\\\"2\\\",\\\"3\\\"]\",\"type\":\"none\"}},{{\"command\":\"[\\\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"테스트 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\",\"type\":\"excel\"}}]"
      },
      {
        "role": "human",
        "text": "[\"A가 B인 것만 남겨\",\"B 컬럼 제거해줘\",\"C가 5 이상인 것만 필터링해\",\"집가고 싶다\"]"
      },
      {
        "role": "ai",
        "text": "[{{\"command\":\"[\\\"A가 B인 것만 남겨\\\",\\\"B 컬럼 제거해줘\\\",\\\"C가 5 이상인 것만 필터링해\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"집가고 싶다\\\"]\",\"type\":\"none\"}}]"
      },
      {
        "role": "human",
        "text": "{cmd_list}"
      }
    ]
```

이런 messages가 있었다면 이걸
``` json
      {
        "system": "당신은 사용자 명령어를 'df'와 'excel', 'none'으로 분류하는 전문가입니다.\n- '템플릿' 또는 'template'이라는 단어가 들어있는 명령만 'excel'로 분류하세요.\n- dataframe을 조작하는 명령(예: 필터링, 포맷 변경 등)은 'df'로 분류하세요.\n- 순수 숫자(0-9)로만 구성된 명령은 'none'으로 분류하세요.\n- 그 외 의미 없는 명령도 'none'으로 분류하세요.\n- 연속된 동일 타입 명령은 하나의 그룹으로 묶습니다.\n  - 연속된 df 명령은 하나의 'df' 그룹으로,\n  - 연속된 none 명령은 하나의 'none' 그룹으로 묶으세요.\n- 순서를 반드시 유지하세요.\n- 각 요소는 반드시 {{'command': '...', 'type': '...'}} 형태의 JSON 객체여야 합니다." ,
        "fewshot" : [
            {
                "human": "[\"4월 5일 이후의 데이터만 필터링 해주세요\",\"defect_rate가 1 이상인 데이터만 필터링 해주세요\",\"1\",\"2\",\"3\",\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\",\"테스트 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\"]",
                "ai": "[{{\"command\":\"[\\\"4월 5일 이후의 데이터만 필터링 해주세요\\\",\\\"defect_rate가 1 이상인 데이터만 필터링 해주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"1\\\",\\\"2\\\",\\\"3\\\"]\",\"type\":\"none\"}},{{\"command\":\"[\\\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"테스트 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\",\"type\":\"excel\"}}]"
            },
            {
                "human": "[\"A가 B인 것만 남겨\",\"B 컬럼 제거해줘\",\"C가 5 이상인 것만 필터링해\",\"집가고 싶다\"]",
                "ai": "[{{\"command\":\"[\\\"A가 B인 것만 남겨\\\",\\\"B 컬럼 제거해줘\\\",\\\"C가 5 이상인 것만 필터링해\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"집가고 싶다\\\"]\",\"type\":\"none\"}}]"
            }
        ],
        "human": "{cmd_list}" 
      }
```
이렇게 fewshot 안에 human과 ai 응답쌍이 들어가게 하는거야. ok?
첫 system과 마지막 human은 system과 human 키로, 중간의 human, ai 응답쌍은 fewshot으로 들어가는거야.
