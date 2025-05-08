from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.redis_client import get_logs_from_redis
from app.utils.dummy import dummy_log
from app.core import auth

router = APIRouter()


@router.get("/{job_id}")
def get_logs(request: Request, job_id: str):
    try:
        user_id = auth.get_user_id_from_header(request)
    except:
        user_id = "guest"

    log_id = f"logs:{user_id}:{job_id}"
    logs = get_logs_from_redis(log_id)
    if not logs:
        # 임시로 없는 로그 조회 시 더미 데이터 표시
        logs = dummy_log
        return JSONResponse(status_code=200, content={"result" : "success", "data" : dummy_log})
        # raise HTTPException(status_code=404, detail="Log not found")
    return JSONResponse(status_code=200, content={"result" : "success", "data" : logs})