from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime

from app.schemas.schedule_schema import (
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
    ScheduleCreateResponse,
    ScheduleUpdateResponse,
    ScheduleDetail,
    PaginatedScheduleListResponse,
    ScheduleListItem,
    FrequencyDisplay,
    RunInfo,
    ToggleResponse,
    ExecuteResponse,
    JobDetail
)
from app.schemas.run_schema import (
    ScheduleRunsResponse,
    RunDetail,
    ScheduleRunDetailResponse,
    JobRunDetail,
    RunSummary,
    ErrorLog
)
from app.schemas.statistics_schema import (
    DailyStatisticsResponse,
    DailyStatItem,
    MonthlyStatisticsResponse,
    MonthlyCalendarData
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


@router.post("", response_model=ScheduleCreateResponse)
async def create_schedule(
        schedule_request: ScheduleCreateRequest,
        user_id: int = Depends(check_admin_permission),
):
    try:
        user_info = auth.get_user_info(user_id)
        user_name = user_info.get('name', 'unknown')

        result = ScheduleService.create_schedule(
            schedule_request=schedule_request,
            user_name=user_name,
            user_id=user_id
        )

        return ScheduleCreateResponse(
            schedule_id=result["schedule_id"],
            created_at=datetime.fromisoformat(result["created_at"]) if isinstance(result["created_at"], str) else
            result["created_at"]
        )

    except Exception as e:
        logger.error(f"Error creating schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 생성에 실패했습니다: {str(e)}")


@router.patch("/{schedule_id}", response_model=ScheduleUpdateResponse)
async def update_schedule(
        schedule_id: str,
        schedule_request: ScheduleUpdateRequest,
        user_id: int = Depends(check_admin_permission),
):
    try:
        user_info = auth.get_user_info(user_id)
        user_name = user_info.get('name', 'unknown')

        result = ScheduleService.update_schedule(
            schedule_id=schedule_id,
            schedule_request=schedule_request,
            user_name=user_name,
            user_id=user_id
        )

        return ScheduleUpdateResponse(
            schedule_id=result["schedule_id"],
            updated_at=datetime.fromisoformat(result["updated_at"]) if isinstance(result["updated_at"], str) else
            result["updated_at"]
        )

    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 업데이트에 실패했습니다: {str(e)}")


@router.get("/statistics/monthly", response_model=MonthlyStatisticsResponse)
async def get_monthly_statistics(
        year: int = Query(...),
        month: int = Query(..., ge=1, le=12),
        user_id: int = Depends(check_admin_permission)
):
    try:
        result = calendar_service.build_monthly_dag_calendar(year, month)

        return MonthlyStatisticsResponse(
            data=MonthlyCalendarData(
                days=result.get("data", {}).get("days", {}),
                summary=result.get("data", {}).get("summary", {}),
                monthly_total=result.get("data", {}).get("monthly_total", {})
            )
        )

    except Exception as e:
        logger.error(f"Error generating calendar data: {e}")
        raise HTTPException(status_code=500, detail=f"달력 데이터 생성에 실패했습니다: {str(e)}")


@router.delete("/statistics/monthly/cache", status_code=200)
async def clear_monthly_statistics_cache(
        year: int = Query(...),
        month: int = Query(..., ge=1, le=12),
        user_id: int = Depends(check_admin_permission)
):
    try:
        # 특정 년월의 캐시만 삭제하는 서비스 메서드 호출
        calendar_service.clear_monthly_cache(year, month)
        return {"message": f"{year}년 {month}월 통계 캐시가 성공적으로 삭제되었습니다."}

    except Exception as e:
        logger.error(f"Error clearing calendar cache: {e}")
        raise HTTPException(status_code=500, detail=f"달력 캐시 삭제에 실패했습니다: {str(e)}")


@router.get("/{schedule_id}", response_model=ScheduleDetail)
async def get_schedule_detail_route(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
):
    try:
        # 서비스 함수 호출
        data = ScheduleService.get_schedule_detail(schedule_id, user_id=user_id)

        # jobs 목록을 JobDetail 객체 리스트로 변환
        jobs = [
            JobDetail(
                id=job.get("id", ""),
                order=job.get("order", 0),
                title=job.get("title", ""),
                description=job.get("description", ""),
                commands=job.get("commands", [])
            ) for job in data.get("jobs", [])
        ]

        return ScheduleDetail(
            schedule_id=data.get("schedule_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            frequency=data.get("frequency", ""),
            frequency_cron=data.get("frequency_cron", ""),
            frequency_display=data.get("frequency_display", ""),
            is_paused=data.get("is_paused", False),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at"),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date"),
            execution_time=data.get("execution_time", ""),
            success_emails=data.get("success_emails", []),
            failure_emails=data.get("failure_emails", []),
            jobs=jobs
        )
    except Exception as e:
        logger.error(f"Error getting schedule detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 상세 조회에 실패했습니다: {str(e)}")


@router.delete("/{schedule_id}", status_code=200)
async def delete_schedule(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
):
    try:
        result = DagService.delete_dag(schedule_id)

        if result:
            return {"message": "스케줄이 삭제되었습니다."}
        else:
            raise HTTPException(status_code=500, detail="스케줄 삭제에 실패했습니다.")
    except Exception as e:
        logger.error(f"Error deleting schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 삭제에 실패했습니다: {str(e)}")


@router.get("/statistics/daily", response_model=DailyStatisticsResponse)
async def get_schedule_executions_by_date(
        year: int = Query(...),
        month: int = Query(..., ge=1, le=12),
        day: int = Query(..., ge=1, le=31),
        user_id: int = Depends(check_admin_permission)
):
    try:
        # 날짜 유효성 검사
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            raise HTTPException(status_code=400, detail="유효하지 않은 날짜입니다. 올바른 날짜를 입력해주세요.")

        response = ScheduleService.get_dag_runs_by_date(date_str)

        # 각 리스트의 아이템을 DailyStatItem으로 변환
        success_items = [DailyStatItem(
            schedule_id=item.get("schedule_id", ""),
            run_id=item.get("run_id"),
            title=item.get("title", ""),
            description=item.get("description", ""),
            owner=item.get("owner", ""),
            status=item.get("status", ""),
            start_time=item.get("start_time"),
            end_time=item.get("end_time"),
            next_run_time=item.get("next_run_time")
        ) for item in response.get("success", [])]

        failed_items = [DailyStatItem(
            schedule_id=item.get("schedule_id", ""),
            run_id=item.get("run_id"),
            title=item.get("title", ""),
            description=item.get("description", ""),
            owner=item.get("owner", ""),
            status=item.get("status", ""),
            start_time=item.get("start_time"),
            end_time=item.get("end_time"),
            next_run_time=item.get("next_run_time")
        ) for item in response.get("failed", [])]

        pending_items = [DailyStatItem(
            schedule_id=item.get("schedule_id", ""),
            run_id=item.get("run_id"),
            title=item.get("title", ""),
            description=item.get("description", ""),
            owner=item.get("owner", ""),
            status=item.get("status", ""),
            start_time=item.get("start_time"),
            end_time=item.get("end_time"),
            next_run_time=item.get("next_run_time")
        ) for item in response.get("pending", [])]

        return DailyStatisticsResponse(
            date=response.get("date", ""),
            success=success_items,
            failed=failed_items,
            pending=pending_items
        )

    except Exception as e:
        logger.error(f"Error getting daily statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"일일 통계 조회에 실패했습니다: {str(e)}")


@router.get("/{schedule_id}/runs", response_model=ScheduleRunsResponse)
async def get_schedule_runs(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
):
    try:
        result = ScheduleService.get_schedule_runs(
            schedule_id, page, size, start_date, end_date
        )

        # runs 리스트를 RunDetail 객체 리스트로 변환
        run_details = [
            RunDetail(
                run_id=run.get("run_id", ""),
                status=run.get("status", ""),
                start_time=run.get("start_time"),
                end_time=run.get("end_time"),
                duration=run.get("duration")
            ) for run in result.get("runs", [])
        ]

        return ScheduleRunsResponse(
            schedule_id=result.get("schedule_id", ""),
            title=result.get("title", ""),
            runs=run_details,
            page=result.get("page", 1),
            size=result.get("size", 10),
            total=result.get("total", 0)
        )
    except Exception as e:
        logger.error(f"Error getting schedule runs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 실행 이력 조회에 실패했습니다: {str(e)}")


@router.get("/{schedule_id}/runs/{run_id}", response_model=ScheduleRunDetailResponse)
async def get_schedule_run_detail(
        schedule_id: str,
        run_id: str,
        user_id: int = Depends(check_admin_permission)
):
    try:
        # 서비스 레이어에서 상세 정보와 로그를 함께 조회
        data = ScheduleService.get_schedule_run_detail_with_logs(schedule_id, run_id, user_id)

        # jobs 목록을 JobRunDetail 객체 리스트로 변환
        job_details = []
        for job in data.get("jobs", []):
            error_log = None
            if job.get("error_log"):
                error_log = ErrorLog(
                    error_message=job["error_log"].get("error_message", ""),
                    error_trace=job["error_log"].get("error_trace"),
                    error_time=job["error_log"].get("error_time"),
                    error_code=job["error_log"].get("error_code")
                )

            job_details.append(JobRunDetail(
                id=job.get("id", ""),
                title=job.get("title", ""),
                description=job.get("description", ""),
                commands=job.get("commands", []),
                status=job.get("status", ""),
                start_time=job.get("start_time"),
                end_time=job.get("end_time"),
                duration=job.get("duration"),
                logs_url=job.get("logs_url", ""),
                error_log=error_log
            ))

        summary = data.get("summary", {})

        return ScheduleRunDetailResponse(
            schedule_id=data.get("schedule_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            run_id=data.get("run_id", ""),
            status=data.get("status", ""),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            duration=data.get("duration"),
            jobs=job_details,
            summary=RunSummary(
                total_jobs=summary.get("total_jobs", 0),
                successful_jobs=summary.get("successful_jobs", 0),
                failed_jobs=summary.get("failed_jobs", 0),
                pending_jobs=summary.get("pending_jobs", 0)
            )
        )
    except Exception as e:
        logger.error(f"Error getting schedule run detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 실행 상세 조회에 실패했습니다: {str(e)}")


@router.post("/{schedule_id}/start", response_model=ExecuteResponse)
async def execute_schedule(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
):
    try:
        result = ScheduleService.execute_schedule(schedule_id)

        return ExecuteResponse(
            schedule_id=result.get("schedule_id", ""),
            run_id=result.get("run_id", ""),
            status=result.get("status", ""),
            execution_date=result.get("execution_date", "")
        )
    except Exception as e:
        logger.error(f"Error executing schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 실행에 실패했습니다: {str(e)}")


@router.patch("/{schedule_id}/toggle", response_model=ToggleResponse)
async def toggle_schedule(
        schedule_id: str,
        user_id: int = Depends(check_admin_permission)
):
    try:
        result = ScheduleService.toggle_schedule(schedule_id)

        return ToggleResponse(
            schedule_id=result.get("schedule_id", ""),
            is_paused=result.get("is_paused", False)
        )
    except Exception as e:
        logger.error(f"Error toggling schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 상태 변경에 실패했습니다: {str(e)}")


@router.get("", response_model=PaginatedScheduleListResponse)
async def get_all_schedules(
        page: int = Query(1, description="페이지 번호", ge=1),
        size: int = Query(20, description="페이지당 항목 수", ge=1, le=100),
        title: str = Query("", description="제목으로 검색"),
        owner: str = Query("", description="소유자로 검색"),
        frequency: str = Query("", description="실행 주기로 검색 (daily, weekly, monthly 등)"),
        status: str = Query("active", description="스케줄 상태로 필터링 (active: 활성화됨, paused: 중지됨, all: 모두)"),
        user_id: int = Depends(check_admin_permission),
):
    try:
        result = ScheduleService.get_all_schedules_with_details(
            user_id=user_id,
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

        # 스케줄 목록을 ScheduleListItem 객체 리스트로 변환
        schedule_items = []
        for schedule in schedules:
            # FrequencyDisplay 객체 생성
            frequency_display = None
            if schedule.get("frequency_display"):
                frequency_display = FrequencyDisplay(
                    type=schedule["frequency_display"].get("type", ""),
                    time=schedule["frequency_display"].get("time", "")
                )

            # RunInfo 객체 생성 (last_run, next_run)
            last_run = None
            if schedule.get("last_run"):
                last_run = RunInfo(
                    run_id=schedule["last_run"].get("run_id"),
                    status=schedule["last_run"].get("status"),
                    end_time=schedule["last_run"].get("end_time")
                )

            next_run = None
            if schedule.get("next_run"):
                next_run = RunInfo(
                    scheduled_time=schedule["next_run"].get("scheduled_time")
                )

            # ScheduleListItem 객체 생성 및 목록에 추가
            schedule_items.append(ScheduleListItem(
                schedule_id=schedule.get("schedule_id", ""),
                title=schedule.get("title", ""),
                description=schedule.get("description", ""),
                is_paused=schedule.get("is_paused", False),
                owner=schedule.get("owner", ""),
                frequency_display=frequency_display,
                jobs=schedule.get("jobs", []),
                last_run=last_run,
                next_run=next_run,
                end_date=schedule.get("end_date")
            ))

        return PaginatedScheduleListResponse(
            schedules=schedule_items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"스케줄 목록 조회에 실패했습니다: {str(e)}")