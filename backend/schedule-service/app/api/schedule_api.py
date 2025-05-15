from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from datetime import datetime, timezone

from app.schemas.schedule_schema import (
    ScheduleCreateRequest,
    ScheduleUpdateRequest
)
# 모듈 단위 import로 변경
from app.services.airflow_client import airflow_client
from app.services.dag_service import DagService
from app.services.schedule_service import ScheduleService
from app.services import calendar_service
from app.utils import cron_utils
from app.core import auth
from app.core.log_config import logger
from app.db import database

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
        db: Session = Depends(database.get_db)
) -> JSONResponse:
    try:
        # frequency를 cron 표현식으로 변환
        cron_expression = cron_utils.convert_frequency_to_cron(
            schedule_request.frequency,
            schedule_request.execution_time,
            schedule_request.start_date
        )

        # 작업 목록 정렬
        sorted_jobs = sorted(schedule_request.jobs, key=lambda job: job.order)
        job_ids = [job.id for job in sorted_jobs]

        # Airflow DAG 생성
        dag_id = DagService.create_dag(
            name=schedule_request.title,
            description=schedule_request.description,
            cron_expression=cron_expression,
            job_ids=job_ids,
            owner=auth.get_user_info(user_id).get('name'),
            start_date=schedule_request.start_date,
            end_date=schedule_request.end_date,
            success_emails=schedule_request.success_emails,
            failure_emails=schedule_request.failure_emails,
            user_id=user_id,
            db=db
        )

        return JSONResponse(status_code=200, content={
            "result": "success",
            "data": {
                "schedule_id": dag_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error creating schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 생성에 실패했습니다: {str(e)}"
        })

@router.get("/statistics/monthly")
async def get_monthly_statistics(
        year: int = Query(...),
        month: int = Query(..., ge=1, le=12),
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        dags = airflow_client.get_all_dags()
        calendar_data = calendar_service.build_monthly_dag_calendar(dags, year, month)

        return JSONResponse(content={
            "result": "success",
            "data": calendar_data
        })
    except Exception as e:
        logger.error(f"Error generating calendar data: {e}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"달력 데이터 생성에 실패했습니다: {str(e)}"
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
        # DAG 삭제
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
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            return JSONResponse(status_code=400, content={
                "result": "error",
                "message": "유효하지 않은 날짜입니다. 올바른 날짜를 입력해주세요."
            })

        dags = airflow_client.get_all_dags()
        executions = ScheduleService.get_dag_runs_by_date(dags, date_str)

        return JSONResponse(content={
            "result": "success",
            "data": executions
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
        # DAG 실행 목록 조회
        dag_runs = airflow_client.get_dag_runs(
            schedule_id,
            limit=page * size,
            start_date=start_date,
            end_date=end_date
        )

        # DAG 상세 정보 조회
        dag_detail = airflow_client.get_dag_detail(schedule_id)

        # 페이징 처리
        total = len(dag_runs)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paged_runs = dag_runs[start_idx:end_idx]

        # 응답 데이터 구성
        run_list = []
        for run in paged_runs:
            run_list.append({
                "run_id": run.get("dag_run_id"),
                "status": run.get("state"),
                "start_time": run.get("start_date"),
                "end_time": run.get("end_date"),
                "duration": (
                        datetime.fromisoformat(run.get("end_date").replace("Z", "+00:00")) -
                        datetime.fromisoformat(run.get("start_date").replace("Z", "+00:00"))
                ).total_seconds() if run.get("end_date") and run.get("start_date") else None
            })

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedule_id": schedule_id,
                "title": dag_detail.get("name", schedule_id),
                "runs": run_list,
                "page": page,
                "size": size,
                "total": total
            }
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
        # DAG 실행
        result = airflow_client.trigger_dag(schedule_id)

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedule_id": schedule_id,
                "run_id": result.get("dag_run_id"),
                "status": result.get("state"),
                "execution_date": result.get("execution_date"),
                "message": "스케줄이 실행되었습니다."
            }
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
        # DAG 상세 정보 조회
        dag_detail = airflow_client.get_dag_detail(schedule_id)

        # 현재 상태 확인 및 토글
        current_state = dag_detail.get("is_paused", False)
        new_state = not current_state

        # DAG 상태 업데이트
        result = airflow_client.toggle_dag_pause(schedule_id, new_state)

        status_message = "일시 중지됨" if new_state else "활성화됨"

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedule_id": schedule_id,
                "is_paused": new_state,
                "message": f"스케줄이 {status_message}입니다."
            }
        })
    except Exception as e:
        logger.error(f"Error toggling schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 상태 변경에 실패했습니다: {str(e)}"
        })

@router.patch("/{schedule_id}")
async def update_schedule(
        schedule_id: str,
        schedule_request: ScheduleUpdateRequest,
        user_id: int = Depends(check_admin_permission)
) -> JSONResponse:
    try:
        # cron 표현식 변환 (frequency가 제공된 경우)
        cron_expression = None
        if schedule_request.frequency and schedule_request.execution_time:
            cron_expression = cron_utils.convert_frequency_to_cron(
                schedule_request.frequency,
                schedule_request.execution_time
            )

        # job_ids 정렬 (jobs가 제공된 경우)
        job_ids = None
        if schedule_request.jobs:
            sorted_jobs = sorted(schedule_request.jobs, key=lambda job: job.order)
            job_ids = [job.id for job in sorted_jobs]

        # DAG 업데이트 - description 제외
        result = DagService.update_dag(
            dag_id=schedule_id,
            name=schedule_request.title,
            # description 필드 제외 (Airflow API에서 읽기 전용)
            # description=schedule_request.description,
            cron_expression=cron_expression,
            job_ids=job_ids,
            start_date=schedule_request.start_date,
            end_date=schedule_request.end_date,
            success_emails=schedule_request.success_emails,
            failure_emails=schedule_request.failure_emails,
            user_id=user_id
        )

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedule_id": schedule_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "message": "스케줄이 업데이트되었습니다."
            }
        })
    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 업데이트에 실패했습니다: {str(e)}"
        })

@router.get("")
async def get_all_schedules(
        user_id: int = Depends(check_admin_permission),
        db: Session = Depends(database.get_db)
) -> JSONResponse:
    """모든 스케줄(DAG) 목록을 반환하는 API"""
    try:
        # 서비스 함수 호출
        result = ScheduleService.get_all_schedules_with_details(user_id=user_id, db=db)

        schedules = result.get("schedules", [])
        total = result.get("total", 0)

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedules": schedules,
                "total": total
            }
        })
    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 목록 조회에 실패했습니다: {str(e)}"
        })