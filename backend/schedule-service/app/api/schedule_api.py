from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.responses import JSONResponse
from datetime import datetime, timezone

from app.schemas.schedule_schema import (
    ScheduleCreateRequest,
    ScheduleUpdateRequest
)
from app.services.airflow_client import airflow_client
from app.services.dag_service import DagService
from app.services.schedule_service import ScheduleService
from app.services import calendar_service
from app.utils import cron_utils
from app.core import auth
from app.core.log_config import logger


router = APIRouter(
    prefix="/api/schedules",
    dependencies=[Depends(auth.get_user_id_from_header)]
)

# ADMIN 권한 체크 함수
def check_admin_permission(user_id: int = Depends(auth.get_user_id_from_header)):
    user_info = auth.get_user_info(user_id)
    if not user_info or user_info.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return user_id


@router.post("")
async def create_schedule(
        schedule_request: ScheduleCreateRequest,
        user_id: int = Depends(check_admin_permission),
) -> JSONResponse:
    try:
        user_info = auth.get_user_info(user_id)
        user_name = user_info.get('name', 'unknown')

        result = ScheduleService.create_schedule(
            schedule_request=schedule_request,
            user_name=user_name,
            user_id=user_id
        )

        return JSONResponse(status_code=200, content={
            "result": "success",
            "data": result
        })

    except Exception as e:
        logger.error(f"Error creating schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 생성에 실패했습니다: {str(e)}"
        })

@router.patch("/{schedule_id}")
async def update_schedule(
        schedule_id: str,
        schedule_request: ScheduleUpdateRequest,
        user_id: int = Depends(check_admin_permission),
        # DB 의존성 제거
) -> JSONResponse:
    try:
        user_info = auth.get_user_info(user_id)
        user_name = user_info.get('name', 'unknown')

        result = ScheduleService.update_schedule(
            schedule_id=schedule_id,
            schedule_request=schedule_request,
            user_name=user_name,
            user_id=user_id
        )

        return JSONResponse(content={
            "result": "success",
            "data": result
        })

    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 업데이트에 실패했습니다: {str(e)}"
        })

@router.get("/statistics/monthly")
async def get_monthly_statistics(
        year: int = Query(...),
        month: int = Query(..., ge=1, le=12),
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        result = calendar_service.build_monthly_dag_calendar(year, month)

        return JSONResponse(content={
            "result": "success",
            "data": result.get("data", {})
        })

    except Exception as e:
        logger.error(f"Error generating calendar data: {e}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"달력 데이터 생성에 실패했습니다: {str(e)}"
        })

@router.delete("/statistics/monthly/cache")
async def clear_monthly_statistics_cache(
        year: int = Query(...),
        month: int = Query(..., ge=1, le=12),
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        # 특정 년월의 캐시만 삭제하는 서비스 메서드 호출
        calendar_service.clear_monthly_cache(year, month)

        return JSONResponse(content={
            "result": "success",
            "message": f"{year}년 {month}월 통계 캐시가 성공적으로 삭제되었습니다.",
        })

    except Exception as e:
        logger.error(f"Error clearing calendar cache: {e}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"달력 캐시 삭제에 실패했습니다: {str(e)}"
        })

@router.get("/{schedule_id}")
async def get_schedule_detail_route(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        # 서비스 함수 호출
        schedule_data = ScheduleService.get_schedule_detail(schedule_id, user_id=user_id)

        return JSONResponse(content={
            "result": "success",
            "data": schedule_data
        })
    except Exception as e:
        logger.error(f"Error getting schedule detail: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 상세 조회에 실패했습니다: {str(e)}"
        })

@router.delete("/{schedule_id}")
async def delete_schedule(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        result = DagService.delete_dag(schedule_id)

        if result:
            return JSONResponse(content={
                "result": "success",
                "message": "스케줄이 삭제되었습니다."
            })
        else:
            return JSONResponse(status_code=500, content={
                "result": "error",
                "message": "스케줄 삭제에 실패했습니다."
            })
    except Exception as e:
        logger.error(f"Error deleting schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 삭제에 실패했습니다: {str(e)}"
        })

@router.get("/statistics/daily")
async def get_schedule_executions_by_date(
        year: int = Query(...),
        month: int = Query(..., ge=1, le=12),
        day: int = Query(..., ge=1, le=31),
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        # 날짜 유효성 검사
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            return JSONResponse(status_code=400, content={
                "result": "error",
                "message": "유효하지 않은 날짜입니다. 올바른 날짜를 입력해주세요."
            })

        response = ScheduleService.get_dag_runs_by_date(date_str)

        return JSONResponse(content={
            "result": "success",
            "data": response
        })

    except Exception as e:
        logger.error(f"Error getting daily statistics: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"일일 통계 조회에 실패했습니다: {str(e)}"
        })

@router.get("/{schedule_id}/runs")
async def get_schedule_runs(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> JSONResponse:
    try:
        result = ScheduleService.get_schedule_runs(
            schedule_id, page, size, start_date, end_date
        )

        return JSONResponse(content={
            "result": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error getting schedule runs: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 실행 이력 조회에 실패했습니다: {str(e)}"
        })

@router.get("/{schedule_id}/runs/{run_id}")
async def get_schedule_run_detail(
        schedule_id: str,
        run_id: str,
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        # 서비스 레이어에서 상세 정보와 로그를 함께 조회
        run_data = ScheduleService.get_schedule_run_detail_with_logs(schedule_id, run_id, user_id)

        return JSONResponse(content={
            "result": "success",
            "data": run_data
        })
    except Exception as e:
        logger.error(f"Error getting schedule run detail: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 실행 상세 조회에 실패했습니다: {str(e)}"
        })

@router.post("/{schedule_id}/start")
async def execute_schedule(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        result = ScheduleService.execute_schedule(schedule_id)

        return JSONResponse(content={
            "result": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error executing schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 실행에 실패했습니다: {str(e)}"
        })

@router.patch("/{schedule_id}/toggle")
async def toggle_schedule(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        result = ScheduleService.toggle_schedule(schedule_id)

        return JSONResponse(content={
            "result": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error toggling schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 상태 변경에 실패했습니다: {str(e)}"
        })

@router.get("")
async def get_all_schedules(
        page: int = Query(1, description="페이지 번호", ge=1),
        size: int = Query(20, description="페이지당 항목 수", ge=1, le=100),
        title: str = Query("", description="제목으로 검색"),  # 기본값 빈 문자열
        owner: str = Query("", description="소유자로 검색"),  # 기본값 빈 문자열
        frequency: str = Query("", description="실행 주기로 검색 (daily, weekly, monthly 등)"),  # 기본값 빈 문자열
        status: str = Query("active", description="스케줄 상태로 필터링 (active: 활성화됨, paused: 중지됨, all: 모두)"),
        user_id: int = Depends(check_admin_permission),
        # DB 의존성 제거
) -> JSONResponse:
    """모든 스케줄(DAG) 목록을 반환하는 API - 필드별 검색 기능 포함 버전"""
    try:
        # 최적화된 서비스 함수 호출 (DB 매개변수 제거)
        result = ScheduleService.get_all_schedules_with_details(
            user_id=user_id,
            # db=db 제거,
            page=page,
            size=size,
            title=title,
            owner=owner,
            frequency=frequency,
            status=status
        )

        schedules = result.get("schedules", [])
        total = result.get("total", 0)

        total_pages = (total + size - 1) // size if total > 0 else 1

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedules": schedules,
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })

    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 목록 조회에 실패했습니다: {str(e)}"
        })