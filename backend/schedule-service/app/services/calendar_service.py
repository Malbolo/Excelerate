from typing import List, Optional, Dict, Any

from croniter import croniter
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
from app.utils import cron_utils, date_utils
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
        calendar_data = build_monthly_dag_calendar(dags, year, month)

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
        user_id: int = Depends(check_admin_permission),
        db: Session = Depends(database.get_db)
) -> JSONResponse:
    try:
        # 서비스 함수 호출 - DB 세션 전달
        schedule_data = ScheduleService.get_schedule_detail(schedule_id, user_id=user_id, db=db)

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
        user_id: int = Depends(check_admin_permission),
        db: Session = Depends(database.get_db)
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
        # DB 세션 전달
        executions = ScheduleService.get_dag_runs_by_date(dags, date_str, db=db)

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
        user_id: int = Depends(check_admin_permission),
        db: Session = Depends(database.get_db)
) -> JSONResponse:
    try:
        # 서비스 레이어에서 상세 정보와 로그를 함께 조회 - DB 세션 전달
        run_data = ScheduleService.get_schedule_run_detail_with_logs(schedule_id, run_id, user_id, db=db)

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
        user_id: int = Depends(check_admin_permission),
        db: Session = Depends(database.get_db)
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
            user_id=user_id,
            db=db  # DB 세션 전달
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
        # 서비스 함수 호출 - DB 세션 전달
        schedules = ScheduleService.get_all_schedules_with_details(
            user_id=user_id,
            db=db
        )

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedules": schedules,
                "total": len(schedules)
            }
        })
    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 목록 조회에 실패했습니다: {str(e)}"
        })

def build_monthly_dag_calendar(dags: List[Dict[str, Any]], year: int, month: int) -> List[Dict[str, Any]]:
    """
    월별 DAG 실행 통계 생성 (현재까지는 실제 실행 이력, 미래는 예측 실행 기반)
    """
    # 타임존을 명시적으로 설정 (UTC 사용)
    first_day, last_day = date_utils.get_month_date_range(year, month)

    # 현재 날짜와 시간
    now = date_utils.get_now_utc()

    # 월의 모든 날짜를 미리 딕셔너리로 초기화
    all_days = []
    for day in range(1, last_day.day + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        all_days.append({
            "date": date_str,
            "total": 0,
            "success": 0,
            "failed": 0,
            "pending": 0
        })

    # 날짜별 데이터 인덱스 구성 (빠른 조회용)
    date_index = {item["date"]: i for i, item in enumerate(all_days)}

    # DAG 별로 처리
    for dag in dags:
        # DAG 활성 상태 확인 - 비활성 DAG는 건너뜁니다
        is_paused = dag.get("is_paused", False)
        if is_paused:
            continue

        dag_id = dag["dag_id"]

        # 스케줄 표현식 추출
        cron_expr = cron_utils.normalize_cron_expression(dag.get("schedule_interval"))

        if not cron_expr or not croniter.is_valid(cron_expr):
            logger.debug(f"Invalid or empty cron: {cron_expr} for DAG {dag_id}")
            continue

        # DAG의 시작일/종료일 추출
        dag_start_date, dag_end_date = _extract_dag_dates(dag, dag_id, now)

        # 범위 체크: 이 달의 날짜와 겹치는지 확인
        if not _is_dag_in_month_range(dag_id, dag_start_date, dag_end_date, first_day, last_day):
            continue

        # 유효한 시작일과 종료일 설정
        effective_start = max(dag_start_date, first_day)
        effective_end = min(dag_end_date, last_day) if dag_end_date else last_day

        if effective_start > effective_end:
            logger.debug(f"{dag_id} effective_start {effective_start} > effective_end {effective_end}")
            continue

        # 실행 이력 조회 (월 전체)
        start_date = date_utils.format_date_for_airflow(first_day)
        end_date = date_utils.format_date_for_airflow(last_day)
        dag_runs = airflow_client.get_dag_runs(dag_id, start_date=start_date, end_date=end_date)

        # 날짜별 실행 이력 구성
        executed_runs_by_date = {}
        for run in dag_runs:
            run_date_str = run.get("start_date", "").split("T")[0]
            if run_date_str:
                if run_date_str not in executed_runs_by_date:
                    executed_runs_by_date[run_date_str] = []
                executed_runs_by_date[run_date_str].append(run)

        # 해당 월의 각 날짜에 대해 데이터 처리
        for date_str, idx in date_index.items():
            # 해당 날짜의 datetime 객체 생성
            date_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            day_start = date_dt.replace(hour=0, minute=0, second=0)
            day_end = date_dt.replace(hour=23, minute=59, second=59)

            # 해당 날짜가 effective_start와 effective_end 사이에 있는지 확인
            if effective_start <= date_dt <= effective_end:
                # 실행 이력 확인
                day_runs = executed_runs_by_date.get(date_str, [])

                # 날짜가 오늘이고 아직 실행 시간이 오지 않았거나, 미래 날짜인 경우 크론 표현식 평가
                if day_end > now:
                    # 오늘의 경우, 현재 시간까지의 실행 이력 처리
                    if day_start <= now <= day_end and day_runs:
                        # 오늘 이미 실행된 것이 있다면 처리
                        success_count = sum(1 for run in day_runs if run.get("state", "").lower() == "success")
                        failed_count = sum(1 for run in day_runs if run.get("state", "").lower() in ["failed", "error"])
                        pending_count = len(day_runs) - success_count - failed_count

                        all_days[idx]["success"] += success_count
                        all_days[idx]["failed"] += failed_count
                        if pending_count > 0:
                            all_days[idx]["pending"] += pending_count

                    # 현재 시간 이후 또는 미래 날짜의 크론 표현식 평가
                    try:
                        # 시작 시간 설정 (오늘의 경우 현재 시간, 미래의 경우 해당 날짜의 시작)
                        start_time = now if day_start <= now <= day_end else day_start

                        # 해당 날짜에 남은 시간에 실행되는 시간 찾기
                        cron_iter = croniter(cron_expr, start_time)
                        execution_time = cron_iter.get_next(datetime)

                        # 같은 날짜 내에 실행 시간이 있는지 확인
                        if execution_time <= day_end and execution_time > now:
                            all_days[idx]["pending"] += 1
                    except Exception as e:
                        logger.debug(f"Error evaluating cron for {dag_id} on {date_str}: {str(e)}")
                else:
                    # 과거 날짜는 실제 실행 이력만 고려
                    if day_runs:
                        success_count = sum(1 for run in day_runs if run.get("state", "").lower() == "success")
                        failed_count = sum(1 for run in day_runs if run.get("state", "").lower() in ["failed", "error"])

                        all_days[idx]["success"] += success_count
                        all_days[idx]["failed"] += failed_count

    # 모든 DAG 처리 후 각 날짜의 total 계산
    for idx, day_data in enumerate(all_days):
        all_days[idx]["total"] = day_data["success"] + day_data["failed"] + day_data["pending"]

    return all_days

def _extract_dag_dates(dag: Dict[str, Any], dag_id: str, now: datetime) -> tuple:
    """DAG의 시작일과 종료일을 추출"""
    # 1. 시작일 추출
    dag_start_date = None
    tags = dag.get("tags", [])

    # 태그에서 시작일 찾기
    for tag in tags:
        tag_value = tag
        if isinstance(tag, dict):
            tag_value = tag.get("name", "")

        if tag_value and tag_value.startswith('start_date:'):
            start_date_str = tag_value.split(':', 1)[1]
            try:
                dag_start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                logger.debug(f"Found start_date in tag for {dag_id}: {dag_start_date}")
                break
            except ValueError:
                pass

    # 시작일을 태그에서 찾지 못한 경우 순차적으로 다른 방법 시도
    if dag_start_date is None:
        dag_start_date = _extract_dag_start_date_from_api(dag, dag_id)

    if dag_start_date is None:
        dag_start_date = date_utils.extract_date_from_dag_id(dag_id)

    if dag_start_date is None:
        dag_start_date = _extract_created_date(dag, now)

    # 2. DAG의 종료일 추출
    dag_end_date = None
    for tag in tags:
        tag_value = tag
        if isinstance(tag, dict):
            tag_value = tag.get("name", "")

        # 종료일 태그 찾기
        if tag_value and tag_value.startswith('end_date:'):
            end_date_str = tag_value.split(':', 1)[1]
            if end_date_str != "None":
                try:
                    dag_end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    pass

    # 종료일을 태그에서 찾지 못한 경우 API 필드 사용
    if dag_end_date is None:
        end_date_str = dag.get("end_date")
        if end_date_str:
            try:
                dag_end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

    return dag_start_date, dag_end_date

def _extract_dag_start_date_from_api(dag: Dict[str, Any], dag_id: str) -> datetime:
    """API 응답에서 시작일 추출"""
    start_date_str = dag.get("start_date")
    if start_date_str:
        try:
            return datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass
    return None


def _extract_created_date(dag: Dict[str, Any], now: datetime) -> datetime:
    """생성일 또는 현재 날짜 사용"""
    created_date_str = dag.get("created")
    if created_date_str:
        try:
            return datetime.fromisoformat(created_date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return now
    return now

def _is_dag_in_month_range(dag_id: str, dag_start_date: datetime, dag_end_date: datetime,
                           first_day: datetime, last_day: datetime) -> bool:
    """DAG가 해당 월의 범위 내에 있는지 확인"""
    # 1. DAG 시작일이 이 달의 마지막 날보다 나중이면 스킵
    if dag_start_date > last_day:
        logger.debug(f"{dag_id} start_date {dag_start_date} is after this month's last day {last_day}")
        return False

    # 2. DAG 종료일이 있고, 이 달의 첫째 날보다 이전이면 스킵
    if dag_end_date and dag_end_date < first_day:
        logger.debug(f"{dag_id} end_date {dag_end_date} is before this month's first day {first_day}")
        return False

    return True