from fastapi import APIRouter, HTTPException, Request, Query, Path
from fastapi.responses import JSONResponse
from app.utils.redis_client import redis_client, get_logs_from_redis, get_logs_data_from_redis
from app.utils.dummy import dummy_log
from app.core import auth
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/{log_id}", summary="특정 로그 세션 조회")
async def get_logs_data(
    request: Request,
    log_id:  str               = Path(..., description="로그 세션 ID (UID)"),
    user_id: Optional[str]     = Query(
        None,
        description="조회할 사용자 ID (생략 시 헤더 또는 'guest')"
    ),
):
    """
    log_id (경로)와 optional user_id (쿼리)를 받아,
    Redis에서 해당 로그 리스트를 꺼내 반환합니다.
    """
    if not user_id:
        user_id = request.headers.get("x-user-id") or "guest"
    # main에선 bearer 토큰을 담아 요청을 보내 x-user-id 활용
    # agent-monitoring에선 user_id랑 log_id 명시

    redis_key = f"logs:{user_id}:{log_id}"
    logs = get_logs_data_from_redis(redis_key)
    if not logs:
        # 임시로 없는 로그 조회 시 더미 데이터 표시
        return JSONResponse(status_code=200, content={"result" : "success", "data" : dummy_log})
        # raise HTTPException(status_code=404, detail="Log not found")
    return JSONResponse(status_code=200, content={"result" : "success", "data" : logs})

@router.get("", summary="유저의 전체 로그 조회") # 보안 설정 필요
async def list_user_logs(
    user_id: Optional[str] = Query(None, description="조회할 사용자 ID")
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
    if user_id:
        pattern = f"logs:*{user_id}*:*"
    else: 
        pattern = f"logs:*:*"
    keys = list(redis_client.scan_iter(match=pattern, count=1000))
    if not keys:
        return JSONResponse(status_code=200, content={"result": "success", "data": []})
    out = []
    for full_key in keys:
        # full_key 예: "logs:alice:abcd1234"
        user = full_key.split(":", 2)[1]
        try:
            user_name = auth.get_user_info(user).name
        except:
            user_name = None
        log_id = full_key.split(":", 2)[2]
        entries = get_logs_from_redis(full_key)
        if entries:
            out.append({
                "user_id": user,
                "user_name":    user_name,
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