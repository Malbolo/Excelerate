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

class QueryDocs:
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
            "data" : [
                {
                    "수원공장": {
                        "system_name": "mes",
                        "factory_id": "FCT001",
                        "product": {
                            "PROD001": {"name":"스마트폰A","category":"전자기기"},
                            "PROD002": {"name":"스마트폰B","category":"전자기기"},
                            "PROD004": {"name":"노트북D","category":"컴퓨터"}
                        },
                        "metric_list": ["defects","production","inventory","energy"]
                    }
                },
                {
                    "평택공장": {
                        "system_name": "smmas",
                        "factory_id": "FCT002",
                        "product": {
                            "PROD003": {"name": "태블릿C", "category": "전자기기"}
                        },
                        "metric_list":  ["defects","production","inventory","energy"]
                    }
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
                "테스트 템플릿을 불러와 dataframe을 1열 5행에 붙여넣고 result로 저장해주세요"
            ],
            "url" : "http://k12s101.p.ssafy.io/api/storage/mes/factory-data/defects?factory_id=FCT001&start_date=2025-04-01&product_code=PROD001"
        }
    }