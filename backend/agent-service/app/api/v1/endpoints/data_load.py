from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.docs import DataDocs
from app.models.query import DataRequest, RagRequest
from app.services.data_load.datachain import FileAPIClient
from app.services.data_load.makerag import CatalogIngestor
from app.core.config import settings
from app.utils.redis_client import generate_log_id, save_logs_to_redis
from app.core import auth

router = APIRouter()
docs = DataDocs()
data_loader = FileAPIClient()

# FastAPI 엔드포인트: 사용자의 질의를 받고 graph를 통해 답변 생성
@router.post("/load")
async def command_code(
    req: Request,
    request: DataRequest = docs.base["data"]
):
    try:
        url, result, logs, code = data_loader.run(request.command)
        user_id = auth.get_user_id_from_header(req) 
        if user_id is None:
            user_id = "guest"
        log_id = generate_log_id(user_id)
        save_logs_to_redis(log_id, logs, metadata={
            "agent_name":  "Data Loader",
            "log_detail":  "데이터를 불러옵니다."
        })
        
        log_id = log_id.split(':')[-1] # 일관성 있게 uid만 반환

    except HTTPException:
        # service에서 던진 HTTPException(400, 502 등)은 그대로 propagate
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"result" : "success", "data" : {"url": url, "dataframe" : result.to_dict(orient="records"), "log_id": log_id, "code": code}})


@router.post("/make")
async def make_rag(
    request: RagRequest = docs.make["data"]
):
    try:
        ingestor = CatalogIngestor(
            catalog_data=request.data,
            connection_args={"host":settings.MILVUS_HOST,"port":settings.MILVUS_PORT},
            collection_name="factory_catalog",
            drop_old=True
        )
        
        ingestor.run()
        
        print("Vector DB 구성 완료")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"result" : "success", "data" : "vector DB 구성됨"})