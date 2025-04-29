from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.docs import DataDocs
from app.models.query import DataRequest


import pandas as pd
from app.services.code_gen.sample import sample_data
df = pd.DataFrame(sample_data["data"]) # 테스트 용

router = APIRouter()
docs = DataDocs()

# FastAPI 엔드포인트: 사용자의 질의를 받고 graph를 통해 답변 생성
@router.post("/")
async def command_code(
    request: DataRequest = docs.base["data"]
):
    try:
        print(request.command)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content=df.to_dict(orient="records"))