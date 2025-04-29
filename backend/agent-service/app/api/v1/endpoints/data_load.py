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
        sample_input = {
            "수원공장": {
                "factory_id": "FCT001",
                "product": {
                "PROD001": {"name":"스마트폰A","category":"전자기기"},
                "PROD002": {"name":"스마트폰B","category":"전자기기"},
                "PROD004": {"name":"노트북D","category":"컴퓨터"}
                },
                "metric_list": ["defects","production","inventory","energy"]
            }
        }

        ingestor = CatalogIngestor(
            catalog_data=sample_input,
            connection_args={"host":"localhost","port":19530},
            collection_name="factory_catalog",
            drop_old=True
        )
        
        ingestor.run()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content="vector DB 구성됨")