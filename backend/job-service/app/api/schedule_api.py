from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.db.database import get_db
from app.schemas.schedule_create_schema import ScheduleCreateRequest
from app.services import schedule_service

router = APIRouter(
    prefix="/api/schedules"
)

@router.post("")
async def create_schedule(request: Request, schedule_request: ScheduleCreateRequest) -> JSONResponse:
    """스케줄 생성 API"""
    user_id = request.headers.get("x-user-id")
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})

    return await schedule_service.create_schedule(schedule_request, user_id)

@router.get("/statistic/monthly")
async def get_monthly_statistics(
    request: Request,
    year: int = Query(..., description="조회할 연도"),
    month: int = Query(..., description="조회할 월", ge=1, le=12),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """월별 스케줄 조회 API"""
    user_id = request.headers.get("x-user-id")
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})

    return await schedule_service.get_monthly_statistics(db, user_id, year, month)

@router.get("/statistics/daily")
async def get_daily_schedules(
    request: Request,
    year: int = Query(..., description="조회할 연도"),
    month: int = Query(..., description="조회할 월", ge=1, le=12),
    day: int = Query(..., description="조회할 일", ge=1, le=31),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """일별 스케줄 목록 조회 API"""
    user_id = request.headers.get("x-user-id")
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})

    return await schedule_service.get_daily_schedules(db, user_id, year, month, day)

@router.get("/{id}")
async def get_schedule_detail(
    id: str,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """스케줄 상세 조회 API"""
    return await schedule_service.get_schedule_detail(db, id)

@router.post("/{id}/status")
async def update_schedule_status(
    id: str,
    status_update: dict,
    db: Session = Depends(get_db)
):
    """스케줄 상태 업데이트 API (Airflow에서 호출)"""
    return await schedule_service.update_schedule_status(db, id, status_update.get("status"))

@router.patch("/{id}/toggle")
async def toggle_schedule(
    request: Request,
    id: str,
    toggle_request: dict,
    db: Session = Depends(get_db)
):
    """스케줄 활성화/비활성화 API"""
    user_id = request.headers.get("x-user-id")
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})

    return await schedule_service.toggle_schedule(db, id, user_id, toggle_request.get("is_active"))