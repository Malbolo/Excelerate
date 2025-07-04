# app/main.py

# FastAPI 서버 기본 설정
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import endpoints
from app.utils.docs import RootDocs
from contextlib import asynccontextmanager
from app.services.code_gen.graph import CodeGenerator
from app.services.data_load.datachain import FileAPIClient
from app.core import auth
from app.utils.api_utils import _DF_SENDER_TASKS
import asyncio

# Lifespan 컨텍스트 매니저로 startup과 shutdown 로직을 한 곳에 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 서비스 인스턴스 생성 및 등록
    app.state.code_gen = CodeGenerator()
    app.state.data_load = FileAPIClient()
    # 필요한 추가 초기화 작업 수행 (예: DB 연결, 캐시 초기화 등)
    yield
    # Shutdown: 종료 로직 수행 (예: 연결 종료 등)
    # 만약 llm_service에 별도의 종료(cleanup) 메서드가 있다면 호출
    if hasattr(app.state.code_gen, "close"):
        await app.state.code_gen.close()
    if hasattr(app.state.data_load, "close"):
        await app.state.data_load.close()
    # 백그라운드 task 모두 종료
    tasks = list(_DF_SENDER_TASKS.values())
    for t in tasks:
        t.cancel()
    # 태스크들이 종료될 때까지 기다림
    await asyncio.gather(*tasks, return_exceptions=True)

app = None

if settings.ENV == "DEV":
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan, docs_url="/api/agent/docs")
else:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan, docs_url="/api/agent/docs", redoc_url=None, openapi_url="/api/agent/openapi.json")
    # app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None) # 배포 시 docs 비활성화

docs = RootDocs()

# CORS 미들웨어 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(endpoints.router, prefix="/api/agent")


@app.get(
    "/api/agent",
    summary="서버 연결 테스트",
    description="루트 디렉토리에 접근해 서버가 활성화되어 있는 지 확인합니다.",
    response_description="서버 상태 코드",
    responses=docs.base["res"],
)
async def read_root(request: Request):
    try:
        user_id = auth.get_user_id_from_header(request) or "guest"

        profile = auth.get_user_info(user_id)
        if profile and isinstance(profile, dict):
            user_name = profile.get("name") or "guest"
        else:
            user_name = "guest"
    except:
        user_name = "guest"
    return JSONResponse(status_code=200, content={"result" : "success", "data" : {"message": f"Hello, {user_name}!"}})
