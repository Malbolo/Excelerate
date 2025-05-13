from fastapi import APIRouter, HTTPException, Request, Query, Path
from fastapi.responses import JSONResponse
from app.utils.redis_client import redis_client, get_logs_from_redis, get_logs_data_from_redis
from app.utils.dummy import dummy_log
from typing import Optional
from datetime import datetime, date
import math

from app.utils.api_utils import get_log_queue
from fastapi.responses import StreamingResponse

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


@router.get("", summary="유저의 전체 로그 조회 (페이지네이션 + 날짜 필터)")
async def list_user_logs(
    user_name: Optional[str]      = Query(None, description="조회할 사용자 이름 (부분검색)"),
    start_date: Optional[str]    = Query(None, description="조회 시작일 (YYYY-MM-DD)"),
    end_date:   Optional[str]    = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
    page:       int               = Query(1, ge=1, description="페이지 번호, 1부터"),
    size:       int               = Query(10, ge=1, le=100, description="한 페이지당 항목 수")
):
    """
    Redis 키 패턴 logs:*{user_name}*:* 에 매칭되는 모든 세션을
    최신순(created_at 내림차순)으로 정렬한 뒤,
    start_date ≤ created_at.date() ≤ end_date 인 것만 남겨서
    page/size 단위로 반환합니다.
    """
    # 0) start/end 날짜 파싱 (빈 문자열 무시)
    if start_date and start_date.strip():
        try:
            start_date = date.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date must be YYYY-MM-DD")

    if end_date and end_date.strip():
        try:
            end_date = date.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date must be YYYY-MM-DD")

    # 1) 키 스캔
    pattern = f"logs:*{user_name}*:*" if user_name else "logs:*:*"
    keys = list(redis_client.scan_iter(match=pattern, count=1000))
    if not keys:
        return JSONResponse({
            "result":     "success",
            "data":       [],
            "pagination": {"page": page, "size": 0, "total": 0, "pages": 0}
        })

    # 2) 전체 결과 수집 + 날짜 필터링
    out: list[dict] = []
    for full_key in keys:
        _, user, log_id = full_key.split(":", 2)
        raw = get_logs_from_redis(full_key) or {}
        meta = raw.get("metadata", {})
        created_iso = meta.get("created_at")
        if not created_iso:
            continue

        # created_at → datetime → date
        created_dt = datetime.fromisoformat(created_iso)
        created_d  = created_dt.date()

        # start_date/end_date 필터링
        if start_date and created_d < start_date:
            continue
        if end_date   and created_d > end_date:
            continue

        out.append({
            "user_name":  user,
            "agent_name": meta.get("agent_name"),
            "log_detail": meta.get("log_detail"),
            "created_at": created_iso,
            "log_id":     log_id,
            "total_latency": meta.get("total_latency")
        })

    # 3) 최신순 정렬
    out.sort(key=lambda x: datetime.fromisoformat(x["created_at"]), reverse=True)

    # 4) 페이지네이션
    total   = len(out)
    pages   = math.ceil(total / size)
    start   = (page - 1) * size
    end     = start + size
    data    = out[start:end]

    return JSONResponse({
        "result": "success",
        "data":   {
            "logs": data,
            "page":  page,
            "size":  len(data),
            "total": total,
            "pages": pages
        }
    })

@router.get("/stream/{stream_id}")
async def stream_logs(request: Request, stream_id: str):
    async def event_generator():
        queue = get_log_queue(stream_id)

        while True:
            if await request.is_disconnected():
                break

            entry = await queue.get()
            data_type = entry["type"]
            data_content = entry["content"]

            # 한 줄씩 yield → ASGI 레벨에서 바로 전송 시도
            yield f"event: {data_type}\n"
            yield f"data: {data_content}\n\n"

    headers = {
        "Cache-Control":       "no-cache",
        "X-Accel-Buffering":   "no"
    }

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=headers
    )