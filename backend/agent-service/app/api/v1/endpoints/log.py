from fastapi import APIRouter, HTTPException, Request, Query, Path
from fastapi.responses import JSONResponse
from app.utils.redis_client import redis_client, get_logs_from_redis, get_logs_data_from_redis
from app.utils.dummy import dummy_log
from typing import Optional
from datetime import datetime
import math

from app.utils.api_utils import get_log_queue
from sse_starlette.sse import EventSourceResponse

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


@router.get("", summary="유저의 전체 로그 조회 (페이지네이션)")
async def list_user_logs(
    user_name: Optional[str] = Query(
        None,
        description="조회할 사용자 이름 (부분검색 가능)"
    ),
    page: int = Query(1, ge=1, description="페이지 번호, 1부터"),
    size: int = Query(10, ge=1, le=100, description="한 페이지당 최대 항목 수")
):
    """
    Redis 키 패턴 logs:*{user_name}*:* 에 매칭되는 모든 세션을\n
    최신순(created_at 내림차순)으로 정렬한 뒤, page/size 단위로 잘라서 아래 형태로 반환합니다.\n
    [{\n
      "user_name":    "사용자 이름",\n
      "agent_name":   "로그를 남긴 Agent의 이름",\n
      "log_detail": "커스텀 상세정보 or 마지막 output",\n
      "createdAt":  "마지막 timestamp 기준",\n
      "log_id":     "해당 세션의 UID"\n
    }, …]
    """
    # 1) 키 스캔
    pattern = f"logs:*{user_name}*:*" if user_name else "logs:*:*"
    keys = list(redis_client.scan_iter(match=pattern, count=1000))

    if not keys:
        return JSONResponse({
            "result":     "success",
            "data":       [],
            "pagination": {
                "page":  page,
                "size":  0,
                "total": 0,
                "pages": 0
            }
        })

    # 2) 전체 결과 수집
    out = []
    for full_key in keys:
        _, user, log_id = full_key.split(":", 2)
        raw = get_logs_from_redis(full_key) or {}
        meta = raw.get("metadata", {})
        out.append({
            "user_name":  user,
            "agent_name": meta.get("agent_name"),
            "log_detail": meta.get("log_detail"),
            "created_at": meta.get("created_at"),
            "log_id":     log_id
        })

    # 3) 최신순 정렬 (ISO 문자열이라 datetime으로 파싱해도, 문자열 정렬만으로도 가능)
    out.sort(
        key=lambda x: datetime.fromisoformat(x["created_at"]),
        reverse=True
    )

    # 4) 페이지네이션 계산
    total   = len(out)
    pages   = math.ceil(total / size)
    start   = (page - 1) * size
    end     = start + size
    page_of = out[start:end]

    return JSONResponse({
        "result": "success",
        "data":   page_of,
        "page":  page,
        "size":  len(page_of),
        "total": total,
    })

@router.get("/stream/{stream_id}")
async def stream_logs(request: Request, stream_id: str):
    queue = get_log_queue(stream_id)

    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            entry = await queue.get()
            data_json = entry.model_dump_json()
            yield {
                "event": "log",
                "data": data_json
            }

    return EventSourceResponse(event_generator())