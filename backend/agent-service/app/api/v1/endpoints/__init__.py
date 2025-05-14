# app/api/v1/endpoints/__init__.py

from fastapi import APIRouter
from app.api.v1.endpoints import query, code_gen, data_load, template, download, log, chatprompt

router = APIRouter()

# # 검색 관련 엔드포인트를 "/query" 경로로 포함
# router.include_router(query.router, prefix="/query", tags=["query"])

# 코드 생성 관련 엔드포인트를 "/data" 경로로 포함
router.include_router(data_load.router, prefix="/data", tags=["data"])

# 코드 생성 관련 엔드포인트를 "/code" 경로로 포함
router.include_router(code_gen.router, prefix="/code", tags=["code"])

router.include_router(template.router, prefix="/template", tags=["template"])

router.include_router(download.router, prefix="/download", tags=["download"])

router.include_router(log.router, prefix="/logs", tags=["logs"])

router.include_router(chatprompt.router, prefix="/prompts", tags=["prompts"])