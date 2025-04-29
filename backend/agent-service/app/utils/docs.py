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

class ExampleDocs:
    base = {
        "res": {
            200: {
                "description": "정상 응답 예시",
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
                "압력에 대한 데이터만 필터링 해주세요.",
                "MACH-001의 데이터만 필터링 해주세요.",
                "collectedAt의 포맷을 YYYY-MM-DD로 변경해주세요."
            ],
            "dataframe": [
                {
                    "machineId": "MACH-001",
                    "parameter": "temperature",
                    "value": 72.5,
                    "unit": "°C",
                    "collectedAt": "2025-04-22T09:44:58Z"
                },
                {
                    "machineId": "MACH-001",
                    "parameter": "pressure",
                    "value": 2.8,
                    "unit": "bar",
                    "collectedAt": "2025-04-23T01:44:58Z"
                },
                {
                    "machineId": "MACH-002",
                    "parameter": "pressure",
                    "value": 2.9,
                    "unit": "bar",
                    "collectedAt": "2025-04-23T02:44:58Z"
                },
                {
                    "machineId": "MACH-003",
                    "parameter": "pressure",
                    "value": 3.1,
                    "unit": "bar",
                    "collectedAt": "2025-04-23T04:21:32Z"
                },
                {
                    "machineId": "MACH-001",
                    "parameter": "speed",
                    "value": 1200,
                    "unit": "rpm",
                    "collectedAt": "2025-04-23T08:41:21Z"
                },
                {
                    "machineId": "MACH-002",
                    "parameter": "speed",
                    "value": 1200,
                    "unit": "rpm",
                    "collectedAt": "2025-04-23T09:44:59Z"
                }
            ]
        }
    }