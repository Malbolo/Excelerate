## Excelerate Agent Server

Excel을 자동화하는 에이전트를 제공하는 FastAPI 서버입니다. LLM을 활용해 DataFrame 조작 코드 생성, Excel 템플릿 삽입, 데이터 로드, 로그 스트리밍 등을 수행합니다.

## 주요 기능

- Chat Prompt 관리: Agent 별 Chat Prompt 템플릿 등록/수정/삭제

- 데이터 로드: RAG를 통한 파라미터 추출 및 Storage-Server API 호출로 데이터 불러오기

- 커맨드 생성: DataFrame 조작(df), Excel 템플릿 삽입(excel), 일반 명령어 처리(none)로 입력된 커맨드를 분류해 코드 생성 및 실행 결과 반환

- Excel 템플릿 관리: MinIO에 템플릿 저장/불러오기 및 미리 보기, 다운로드 지원

- 로그 스트리밍: SSE(Server-Sent Events)를 이용한 실시간 로그 전송

- 인증 & 권한: Auth-Server를 통해 JWT 기반 인증 지원

- Redis: 로그 및 Chat Prompt 관리

- MinIO: 템플릿 저장 및 결과 업로드

## 기술 스택

- Python 3.10+

- FastAPI, Uvicorn

- Redis

- MinIO

- LangChain

- LangGraph

## 프로젝트 디렉토리 구조

```
agent-service
├─ app
│  ├─ api
│  │  └─ v1
│  │     └─ endpoints
│  │        ├─ chatprompt.py
│  │        ├─ code_gen.py
│  │        ├─ data_load.py
│  │        ├─ download.py
│  │        ├─ log.py
│  │        ├─ template.py
│  │        └─ __init__.py
│  ├─ core
│  │  ├─ auth.py
│  │  ├─ config.py
│  │  └─ __init__.py
│  ├─ main.py
│  ├─ models
│  │  ├─ chatprompt.py
│  │  ├─ log.py
│  │  ├─ query.py
│  │  ├─ structure.py
│  │  └─ __init__.py
│  ├─ services
│  │  ├─ chatprompt_service.py
│  │  ├─ code_gen
│  │  │  ├─ graph.py
│  │  │  ├─ graph_image
│  │  │  │  └─ output.png
│  │  │  ├─ graph_util.py
│  │  │  ├─ merge_utils.py
│  │  │  └─ readme.md
│  │  ├─ data_load
│  │  │  ├─ datachain.py
│  │  │  ├─ data_util.py
│  │  │  └─ makerag.py
│  │  ├─ template.py
│  │  └─ __init__.py
│  └─ utils
│     ├─ api_utils.py
│     ├─ depend.py
│     ├─ docs.py
│     ├─ memory_logger.py
│     ├─ minio_client.py
│     ├─ promptmaker.md
│     ├─ redis_chatprompt.py
│     ├─ redis_client.py
│     └─ __init__.py
├─ Dockerfile
├─ readme.md
└─ requirements.txt
```

## 프로젝트 초기 설정
1. 공장 정보 vector DB 등록
`POST` `/api/agent/data/make` API를 사용해 공장 정보를 Milvus에 등록합니다.
다음과 같은 구조로 등록하면 됩니다.
``` json
{
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
        }
    ]
}
```
실 서비스에선 더미 데이터가 아닌 MES와 연결해 사용하므로 대체하시면 좋습니다.


2. Agent 별 ChatPrompt 등록
`POST` `/api/agent/prompts` API를 사용해 utils 폴더 내의 promptmaker.md에 있는 내용을 서버의 Redis에 등록합니다.
총 6개의 프롬프트를 등록하시면 됩니다.

Code Generator
- Generate Code Extension
- Generate Code
- Manipulate Excel
- Split Command List

Data Loader
- Extract DataCall Params
- Transform Date Params


## 로깅 메커니즘
app/utils/memory_logger.py 를 활용해 로그를 남기고자 하는 llm의 로그를 수집합니다.
llm 시작 시 prompt와 시간을 저장하고, llm 종료 시 output과 지연 시간, 메타데이터를 log 형태로 저장합니다.

logger에 저장된 로그는 redis와 log_queue를 이용해 저장 및 스트리밍 됩니다.

1. LLM 호출 시 logger를 callbacks로 지정한다.
``` py
class CodeGenerator:
    def __init__(self):
        self.logger = MemoryLogger()
        self.minio_client = MinioClient()
        self.sllm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0, callbacks=[self.logger])
        self.q = None
```

2. 이 후 LLM 호출을 시작 위치에서 logger를 초기화하고, 호출이 끝난 후 logger의 데이터를 불러와 저장한다.
``` py
# logger 초기화 - /service/code_gen/graph.py line 63
self.logger.set_name("LLM Call: Split Command List")
self.logger.reset()

... # LLM invoke 작업 수행

# log 저장 - - /service/code_gen/graph.py line 125
llm_entry = self.logger.get_logs()[-1] if self.logger.get_logs() else None
new_logs  = state.get("logs", []) + ([llm_entry] if llm_entry else [])
```

3. 필요한 위치에서 로그를 스트리밍하고, 호출 종료 시 Redis에 metadata를 붙여 저장한다.
``` py
# 큐 불러오기 - /service/code_gen/graph.py line 65
self.q = get_log_queue(state["stream_id"])

# stream_id로 쏘기 - /service/code_gen/graph.py line 128
if llm_entry:
    log = log_filter(llm_entry)
    self.q.put_nowait({"type": "log", "content": log})

# Redis에 로그 저장하기 - /api/v1/endpoints/code_gen.py line 93
save_logs_to_redis(log_id, answer["logs"], metadata={
    "agent_name":  "Code Generetor",
    "log_detail":  "코드를 생성합니다.",
    "total_latency": api_latency
})
```

저장되는 로그의 구조는 다음과 같습니다.
``` json
{
    "metadata": {
        "agent_name": "Data Loader",
        "log_detail": "데이터를 불러옵니다.",
        "total_latency": 3.824995,
        "created_at": "2025-05-20T00:07:54.259770+00:00"
    },
    "logs": [
        {
            "name": "LLM Call: Extract DataCall Params",
            "input": [
                {"role": "system", "message": "시스템 메시지"},
                {"role": "human", "message": "휴먼 메시지"}
            ],
            "output": [
                {"role": "ai", "message": "AI 메시지"}
            ],
            "timestamp": "2025-05-20T00:07:53.326562Z",
            "metadata": {
                "token_usage": {
                    "completion_tokens": 48,
                    "prompt_tokens": 958,
                    "total_tokens": 1006,
                    "completion_tokens_details": {
                        "accepted_prediction_tokens": 0,
                        "audio_tokens": 0,
                        "reasoning_tokens": 0,
                        "rejected_prediction_tokens": 0
                    },
                    "prompt_tokens_details": {
                        "audio_tokens": 0,
                        "cached_tokens": 0
                    }
                },
                "model_name": "gpt-4.1-mini-2025-04-14",
                "system_fingerprint": "fp_79b79be41f",
                "id": "chatcmpl-BZ4oHHTQjnhgGGiLkRGbaZzCctfTe",
                "finish_reason": "stop",
                "logprobs": null,
                "llm_latency": 2.19126
            },
            "sub_events": []
        }
    ]
}
```

