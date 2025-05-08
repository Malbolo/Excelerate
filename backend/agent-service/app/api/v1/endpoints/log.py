from fastapi import APIRouter, HTTPException, Request, Query, Path
from fastapi.responses import JSONResponse
from app.utils.redis_client import redis_client, get_logs_from_redis, get_logs_data_from_redis
from app.utils.dummy import dummy_log
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/{log_id}", summary="특정 로그 세션 조회 (user_id 없이)")
async def get_logs_data(
    log_id: str = Path(..., description="로그 세션 ID (UID)")
):
    """
    log_id만으로 Redis 키 패턴 logs:*:{log_id} 에 매칭되는
    첫번째 세션을 찾아 그 안의 로그 리스트를 반환합니다.
    """
    # 1) 패턴 매칭으로 일치하는 키 찾기
    pattern = f"logs:*:{log_id}"
    matches = list(redis_client.scan_iter(match=pattern, count=1000))
    if not matches:
        return JSONResponse(status_code=200, content={
            "result": "success",
            "data":   dummy_log
        })

    # 2) 첫번째 매칭된 키로 조회
    redis_key = matches[0]
    logs = get_logs_data_from_redis(redis_key)
    if not logs:
        return JSONResponse(status_code=200, content={
            "result": "success",
            "data":   dummy_log
        })

    # 3) 정상 응답
    return JSONResponse(status_code=200, content={
        "result": "success",
        "data":   logs
    })



@router.get("", summary="유저의 전체 로그 조회") # 보안 설정 필요
async def list_user_logs(
    user_name: Optional[str] = Query(None, description="조회할 사용자 이름")
):
    """
    Redis 키 패턴 logs:{user_id}:* 에 매칭되는
    모든 log_id 세션을 찾아, 그 안의 LogDetail을 아래 형태로 반환합니다:

    [{
      "user_id":    "사용자 ID",
      "agent_name":   "로그를 남긴 Agent의 이름",
      "log_detail": "커스텀 상세정보 or 마지막 output",
      "createdAt":  "마지막 timestamp 기준",
      "log_id":     "해당 세션의 UID"
    }, …]
    """
    if user_name:
        pattern = f"logs:*{user_name}*:*"
    else: 
        pattern = f"logs:*:*"
    keys = list(redis_client.scan_iter(match=pattern, count=1000))
    if not keys:
        return JSONResponse(status_code=200, content={"result": "success", "data": []})
    out = []
    for full_key in keys:
        # full_key 예: "logs:alice:abcd1234"
        user = full_key.split(":", 2)[1]
        log_id = full_key.split(":", 2)[2]
        entries = get_logs_from_redis(full_key)
        if entries:
            out.append({
                "user_name":    user,
                "agent_name":   entries["metadata"].get("agent_name"),
                "log_detail": entries["metadata"].get("log_detail"),
                "created_at":  entries["metadata"].get("created_at"),
                "log_id":     log_id
            })

    out.sort(
        key=lambda item: datetime.fromisoformat(item["created_at"]),
        reverse=True
    )

    return JSONResponse(status_code=200, content={"result": "success", "data": out})