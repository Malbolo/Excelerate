from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.docs import DataDocs
from app.models.query import DataRequest
from app.services.data_load.datachain import FileAPIClient
from app.services.data_load.makerag import CatalogIngestor

router = APIRouter()
docs = DataDocs()
data_loader = FileAPIClient()

# FastAPI 엔드포인트: 사용자의 질의를 받고 graph를 통해 답변 생성
@router.post("/load")
async def command_code(
    request: DataRequest = docs.base["data"]
):
    try:
        url, result = data_loader.run(request.command)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"url": url, "data" : result.to_dict(orient="records")})


@router.get("/make")
async def make_rag():
    try:
        set_rag = CatalogIngestor()
        set_rag.run()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content="vector DB 구성됨")