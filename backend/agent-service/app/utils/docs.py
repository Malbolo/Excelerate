# app/utils/docs.py

class RootDocs:
    base = {
        "res": {
            200: {
                "description": "서버 활성화",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Hello, FastAPI!"
                        }
                    }
                },
            },
            400: {"description": "잘못된 요청"}
        }
    }

class DataDocs:
    base = {
        "res": {
            200: {
                "description": "쿼리 응답",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "대답이 텍스트로 표시됩니다."
                        }
                    }
                },
            },
            400: {"description": "잘못된 요청"}
        },
        "data" : {
            "command": "수원공장에서 4월 1일 부터 스마트폰A 불량률 데이터 가져와"
        }
    }
    make = {
        "data": {
            "data": [
                {
                    "factory_name": "수원공장",
                    "system_name": "mes",
                    "factory_id": "FCT001",
                    "product": {
                        "PROD001": { "name": "스마트폰A", "category": "전자기기" },
                        "PROD002": { "name": "스마트폰B", "category": "전자기기" },
                        "PROD004": { "name": "노트북D", "category": "컴퓨터"   }
                    },
                    "metric_list": ["defects", "production", "inventory", "energy"]
                },
                {
                    "factory_name": "평택공장",
                    "system_name": "mes",
                    "factory_id": "FCT002",
                    "product": {
                        "PROD003": { "name": "태블릿C", "category": "전자기기" },
                        "PROD005": { "name": "데스크탑E", "category": "컴퓨터" }
                    },
                    "metric_list": ["defects", "production", "inventory", "energy"]
                },
                {
                    "factory_name": "구미공장",
                    "system_name": "mes",
                    "factory_id": "FCT003",
                    "product": {
                        "PROD002": { "name": "스마트폰B", "category": "전자기기" },
                        "PROD004": { "name": "노트북D", "category": "컴퓨터"   }
                    },
                    "metric_list": ["defects", "production", "inventory", "energy"]
                }
            ]
        }
    }

class CodeGenDocs:
    base = {
        "res": {
            200: {
                "description": "쿼리 응답",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "대답이 텍스트로 표시됩니다."
                        }
                    }
                },
            },
            400: {"description": "잘못된 요청"}
        },
        "data" : {
            "command_list": [
                "4월 5일 이후의 데이터만 필터링 해주세요.",
                "defect_rate가 1 이상인 데이터만 필터링 해주세요.",
                "날짜의 포맷을 YYYY-MM-DD로 변경해주세요.",
                "불량률 현황 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요"
            ],
            "url" : "http://k12s101.p.ssafy.io/api/storage/mes/factory-data/defects?factory_id=FCT001&start_date=2025-04-01&product_code=PROD001"
        }
    }

class ChatDocs:
    invoke = {
        "res": {
            200: {
                "description": "쿼리 응답",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "대답이 텍스트로 표시됩니다."
                        }
                    }
                },
            },
            400: {"description": "잘못된 요청"}
        },
        "excel" : {
            "messages": [
                {
                "role": "system",
                "text": "사용자 명령어에서 엑셀 템플릿 이름, 시트 이름(선택), 삽입 시작 위치, 결과 파일명을 JSON으로 추출해 주세요.\n\n예시)\n\"KPIreport 템플릿을 불러와서 3열 4행부터 데이터를 꽉 차게 삽입한 뒤 KPI_결과.xlsx로 저장해줘\"\n{{\n  \"template_name\": \"KPIreport\",\n  \"sheet_name\": null,\n  \"start_row\": 4,\n  \"start_col\": 3,\n  \"output_name\": \"KPI_결과.xlsx\"\n}}"
                },
                {
                "role": "human",
                "text": "{command}"
                }
            ],
            "variables": {"command":"불량률 현황 템플릿에 1열 5행에 붙여넣어줘"}
        },
        "split" : {
            "messages": {
                "system": "당신은 사용자 명령어를 'df'와 'excel', 'none'으로 분류하는 전문가입니다.\n- '템플릿' 또는 'template'이라는 단어가 들어있는 명령만 'excel'로 분류하세요.\n- dataframe을 조작하는 명령(예: 필터링, 포맷 변경 등)은 'df'로 분류하세요.\n- 순수 숫자(0-9)로만 구성된 명령은 'none'으로 분류하세요.\n- 그 외 의미 없는 명령도 'none'으로 분류하세요.\n- 연속된 동일 타입 명령은 하나의 그룹으로 묶습니다.\n  - 연속된 df 명령은 하나의 'df' 그룹으로,\n  - 연속된 none 명령은 하나의 'none' 그룹으로 묶으세요.\n- 순서를 반드시 유지하세요.\n- 각 요소는 반드시 {{'command': '...', 'type': '...'}} 형태의 JSON 객체여야 합니다.",
                "fewshot": [
                {
                    "human": "[\"4월 5일 이후의 데이터만 필터링 해주세요\",\"defect_rate가 1 이상인 데이터만 필터링 해주세요\",\"1\",\"2\",\"3\",\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\",\"불량률 현황 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\"]",
                    "ai": "[{{\"command\":\"[\\\"4월 5일 이후의 데이터만 필터링 해주세요\\\",\\\"defect_rate가 1 이상인 데이터만 필터링 해주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"1\\\",\\\"2\\\",\\\"3\\\"]\",\"type\":\"none\"}},{{\"command\":\"[\\\"날짜의 포맷을 YYYY-MM-DD로 변경해 주세요\\\"]\",\"type\":\"df\"}},{{\"command\":\"불량률 현황 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요\",\"type\":\"excel\"}}]"
                },
                {
                    "human": "[\"A가 B인 것만 남겨\",\"B 컬럼 제거해줘\",\"C가 5 이상인 것만 필터링해\",\"집가고 싶다\"]",
                    "ai": "[{{\"command\":\"[\\\"A가 B인 것만 남겨\\\",\\\"B 컬럼 제거해줘\\\",\\\"C가 5 이상인 것만 필터링해\\\"]\",\"type\":\"df\"}},{{\"command\":\"[\\\"집가고 싶다\\\"]\",\"type\":\"none\"}}]"
                }
                ],
                "human": "{cmd_list}"
            },
            "variables": {
                "cmd_list": [
                "불량률 1 이상만 필터링해줘",
                "집가고 싶다.",
                "불량률 현황 템플릿에 1열 5행에 붙여넣어"
                ]
            }
        },
        "template" : {
            "template_name": "Code Generator:Split Command List",
            "variables": {
                "cmd_list": [
                "불량률 1 이상만 필터링해줘",
                "집가고 싶다.",
                "불량률 현황 템플릿에 1열 5행에 붙여넣어"
                ]
            }
        }
    }