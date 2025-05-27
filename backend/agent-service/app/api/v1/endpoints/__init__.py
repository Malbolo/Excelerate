# app/api/v1/endpoints/__init__.py

from fastapi import APIRouter
from app.api.v1.endpoints import code_gen, data_load, template, download, log, chatprompt

router = APIRouter()

router.include_router(data_load.router, prefix="/data", tags=["data"])

router.include_router(code_gen.router, prefix="/code", tags=["code"])

router.include_router(template.router, prefix="/template", tags=["template"])

router.include_router(download.router, prefix="/download", tags=["download"])

router.include_router(log.router, prefix="/logs", tags=["logs"])

router.include_router(chatprompt.router, prefix="/prompts", tags=["prompts"])