from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.docs import DataDocs
from app.models.query import DataRequest
from app.services.data_load.datachain import FileAPIClient


import pandas as pd

router = APIRouter()
docs = DataDocs()
data_loader = FileAPIClient()

# FastAPI 엔드포인트: 사용자의 질의를 받고 graph를 통해 답변 생성
@router.post("/load")
async def command_code(
    request: DataRequest = docs.base["data"]
):
    try:
        result = data_loader.run(request.command)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content=result.to_dict(orient="records"))