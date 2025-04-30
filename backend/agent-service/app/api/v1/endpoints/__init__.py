# app/api/v1/endpoints/__init__.py

from fastapi import APIRouter
from app.api.v1.endpoints import example, query, code_gen, data_load

router = APIRouter()

# # 검색 관련 엔드포인트를 "/example" 경로로 포함
# router.include_router(example.router, prefix="/example", tags=["example"])

# # 검색 관련 엔드포인트를 "/query" 경로로 포함
# router.include_router(query.router, prefix="/query", tags=["query"])

# 코드 생성 관련 엔드포인트를 "/data" 경로로 포함
router.include_router(data_load.router, prefix="/data", tags=["data"])

# 코드 생성 관련 엔드포인트를 "/code" 경로로 포함
router.include_router(code_gen.router, prefix="/code", tags=["code"])
