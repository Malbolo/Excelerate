from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.redis_client import get_logs_from_redis
from app.utils.dummy import dummy_log

router = APIRouter()


@router.get("/{job_id}")
def get_logs(job_id: str, user_id: str = "guest"):
    log_id = f"logs:{user_id}:{job_id}"
    logs = get_logs_from_redis(log_id)
    if not logs:
        # 임시로 없는 로그 조회 시 더미 데이터 표시
        logs = dummy_log
        return JSONResponse(status_code=200, content={"result" : "success", "data" : dummy_log})
        # raise HTTPException(status_code=404, detail="Log not found")
    return JSONResponse(status_code=200, content={"result" : "success", "data" : logs})