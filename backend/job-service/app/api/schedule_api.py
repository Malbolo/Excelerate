import os
from typing import List, Optional
from fastapi import APIRouter, Request, Query, HTTPException
from starlette.responses import JSONResponse
from datetime import datetime
from app.schemas.schedule_schema import (
    ScheduleCreateRequest, 
    ScheduleUpdateRequest
)
from app.services import airflow_service
from app.core import auth

router = APIRouter(
    prefix="/api/schedules"
)

@router.post("")
async def create_schedule(request: Request, schedule_request: ScheduleCreateRequest) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)

    try:
        # frequency를 cron 표현식으로 변환
        cron_expression = _convert_frequency_to_cron(
            schedule_request.frequency,
            schedule_request.execution_time,
            schedule_request.start_date
        )

        # 작업 목록 정렬
        sorted_jobs = sorted(schedule_request.jobs, key=lambda job: job.order)
        job_ids = [job.id for job in sorted_jobs]

        # Airflow DAG 생성
        dag_id = airflow_service.create_dag(
            name=schedule_request.title,
            description=schedule_request.description,
            cron_expression=cron_expression,
            job_ids=job_ids,
            owner=f"user_{user_id}",
            start_date=schedule_request.start_date,
            end_date=schedule_request.end_date,
            success_emails=schedule_request.success_emails,
            failure_emails=schedule_request.failure_emails
        )

        return JSONResponse(status_code=200, content={
            "result": "success",
            "data": {
                "schedule_id": dag_id,
                "created_at": datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"Error creating schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 생성에 실패했습니다: {str(e)}"
        })

@router.get("/statistics/monthly")
async def get_monthly_statistics(
    request: Request,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12)
) -> JSONResponse:
    try:
        dags = airflow_service.get_all_dags()
        calendar_data = airflow_service.build_monthly_dag_calendar(dags, year, month)

        return JSONResponse(content={
            "result": "success",
            "data": calendar_data
        })
    except Exception as e:
        print(f"Error generating calendar data: {e}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"달력 데이터 생성에 실패했습니다: {str(e)}"
        })

@router.get("/{schedule_id}")
async def get_schedule_detail(request: Request, schedule_id: str) -> JSONResponse:
    try:
        # 서비스 함수 호출
        schedule_data = airflow_service.get_schedule_detail(schedule_id)

        return JSONResponse(content={
            "result": "success",
            "data": schedule_data
        })
    except Exception as e:
        print(f"Error getting schedule detail: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 상세 조회에 실패했습니다: {str(e)}"
        })

@router.delete("/{schedule_id}")
async def delete_schedule(request: Request, schedule_id: str) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")
        tags = [tag["name"] if isinstance(tag, dict) else tag for tag in dag_detail.get("tags", [])]
        if owner != dag_owner and owner not in tags:
            return JSONResponse(status_code=403, content={
                "result": "error",
                "message": "해당 스케줄에 삭제 권한이 없습니다."
            })
        
        # DAG 삭제
        result = airflow_service.delete_dag(schedule_id)
        
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
        print(f"Error deleting schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 삭제에 실패했습니다: {str(e)}"
        })



@router.get("/statistics/daily")
async def get_schedule_executions_by_date(
    request: Request,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    day: int = Query(..., ge=1, le=31)
) -> JSONResponse:
    try:
        # 날짜 유효성 검사
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return JSONResponse(status_code=400, content={
                "result": "error",
                "message": "유효하지 않은 날짜입니다. 올바른 날짜를 입력해주세요."
            })

        dags = airflow_service.get_all_dags()
        executions = airflow_service.get_dag_runs_by_date(dags, date_str)

        return JSONResponse(content={
            "result": "success",
            "data": executions
        })

    except Exception as e:
        print(f"Error getting daily statistics: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"일일 통계 조회에 실패했습니다: {str(e)}"
        })



@router.get("/{schedule_id}/runs")
async def get_schedule_runs(
    request: Request,
    schedule_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)

        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")

        # 태그에서 소유자 확인
        tags = dag_detail.get("tags", [])
        # 태그가 문자열 또는 딕셔너리 형태로 올 수 있음
        tag_values = []
        for tag in tags:
            if isinstance(tag, dict) and "name" in tag:
                tag_values.append(tag["name"])
            else:
                tag_values.append(tag)

        # 현재 사용자가 소유자인지 또는 태그에 포함되어 있는지 확인
        if owner != dag_owner and owner not in tag_values:
            return JSONResponse(status_code=403, content={
                "result": "error",
                "message": "해당 스케줄에 접근 권한이 없습니다."
            })

        # DAG 실행 목록 조회
        dag_runs = airflow_service.get_dag_runs(
            schedule_id,
            limit=page * size,
            start_date=start_date,
            end_date=end_date
        )

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
        print(f"Error getting schedule runs: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 실행 이력 조회에 실패했습니다: {str(e)}"
        })

@router.get("/{schedule_id}/runs/{run_id}")
async def get_schedule_run_detail(
    request: Request,
    schedule_id: str,
    run_id: str
) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)

        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")

        # 태그에서 소유자 확인
        tags = dag_detail.get("tags", [])
        # 태그가 문자열 또는 딕셔너리 형태로 올 수 있음
        tag_values = []
        for tag in tags:
            if isinstance(tag, dict) and "name" in tag:
                tag_values.append(tag["name"])
            else:
                tag_values.append(tag)

        # 현재 사용자가 소유자인지 또는 태그에 포함되어 있는지 확인
        if owner != dag_owner and owner not in tag_values:
            return JSONResponse(status_code=403, content={
                "result": "error",
                "message": "해당 스케줄에 접근 권한이 없습니다."
            })

        # DAG 실행 상세 정보 조회
        run_detail = airflow_service.get_dag_run_detail(schedule_id, run_id)

        # 태스크 인스턴스 목록 조회
        task_instances = airflow_service.get_task_instances(schedule_id, run_id)

        # 태스크 데이터 구성
        task_list = []
        for task in task_instances:
            task_id = task.get("task_id", "")

            # job_id 추출 (task_id 형식: 'job_1' 등)
            job_id = None
            if task_id.startswith("job_"):
                try:
                    job_id = task_id.split("_")[1]
                except (IndexError, ValueError):
                    pass

            task_list.append({
                "task_id": task_id,
                "job_id": job_id,
                "status": task.get("state"),
                "start_time": task.get("start_date"),
                "end_time": task.get("end_date"),
                "duration": task.get("duration"),
                "logs_url": f"{airflow_service.settings.AIRFLOW_API_URL}/dags/{schedule_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs"
            })

        # 응답 데이터 구성
        run_data = {
            "schedule_id": schedule_id,
            "title": dag_detail.get("name", schedule_id),  # schedule_name → title로 변경
            "run_id": run_id,
            "status": run_detail.get("state"),
            "start_time": run_detail.get("start_date"),
            "end_time": run_detail.get("end_date"),
            "duration": (
                    datetime.fromisoformat(run_detail.get("end_date").replace("Z", "+00:00")) -
                    datetime.fromisoformat(run_detail.get("start_date").replace("Z", "+00:00"))
            ).total_seconds() if run_detail.get("end_date") and run_detail.get("start_date") else None,
            "tasks": task_list
        }

        return JSONResponse(content={
            "result": "success",
            "data": run_data
        })
    except Exception as e:
        print(f"Error getting schedule run detail: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 실행 상세 조회에 실패했습니다: {str(e)}"
        })

@router.post("/{schedule_id}/start")
async def execute_schedule(request: Request, schedule_id: str) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)

        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")

        # 태그에서 소유자 확인
        tags = dag_detail.get("tags", [])
        # 태그가 문자열 또는 딕셔너리 형태로 올 수 있음
        tag_values = []
        for tag in tags:
            if isinstance(tag, dict) and "name" in tag:
                tag_values.append(tag["name"])
            else:
                tag_values.append(tag)

        # 현재 사용자가 소유자인지 또는 태그에 포함되어 있는지 확인
        if owner != dag_owner and owner not in tag_values:
            return JSONResponse(status_code=403, content={
                "result": "error",
                "message": "해당 스케줄에 실행 권한이 없습니다."
            })

        # DAG 실행
        result = airflow_service.trigger_dag(schedule_id)

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
        print(f"Error executing schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 실행에 실패했습니다: {str(e)}"
        })

@router.patch("/{schedule_id}/toggle")
async def toggle_schedule(
    request: Request, 
    schedule_id: str
) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")

        # 태그에서 소유자 확인
        tags = dag_detail.get("tags", [])
        # 태그가 문자열 또는 딕셔너리 형태로 올 수 있음
        tag_values = []
        for tag in tags:
            if isinstance(tag, dict) and "name" in tag:
                tag_values.append(tag["name"])
            else:
                tag_values.append(tag)

        # 현재 사용자가 소유자인지 또는 태그에 포함되어 있는지 확인
        if owner != dag_owner and owner not in tag_values:
            return JSONResponse(status_code=403, content={
                "result": "error",
                "message": "해당 스케줄에 변경 권한이 없습니다."
            })
        
        # 현재 상태 확인 및 토글
        current_state = dag_detail.get("is_paused", False)
        new_state = not current_state
        
        # DAG 상태 업데이트
        result = airflow_service.toggle_dag_pause(schedule_id, new_state)
        
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
        print(f"Error toggling schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 상태 변경에 실패했습니다: {str(e)}"
        })


@router.patch("/{schedule_id}")
async def update_schedule(
        request: Request,
        schedule_id: str,
        schedule_request: ScheduleUpdateRequest
) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)

        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")

        # 태그에서 소유자 확인
        tags = dag_detail.get("tags", [])
        # 태그가 문자열 또는 딕셔너리 형태로 올 수 있음
        tag_values = []
        for tag in tags:
            if isinstance(tag, dict) and "name" in tag:
                tag_values.append(tag["name"])
            else:
                tag_values.append(tag)

        # 현재 사용자가 소유자인지 또는 태그에 포함되어 있는지 확인
        if owner != dag_owner and owner not in tag_values:
            return JSONResponse(status_code=403, content={
                "result": "error",
                "message": "해당 스케줄에 변경 권한이 없습니다."
            })

        # cron 표현식 변환 (frequency가 제공된 경우)
        cron_expression = None
        if schedule_request.frequency and schedule_request.execution_time:
            cron_expression = _convert_frequency_to_cron(
                schedule_request.frequency,
                schedule_request.execution_time
            )

        # job_ids 정렬 (jobs가 제공된 경우)
        job_ids = None
        if schedule_request.jobs:
            sorted_jobs = sorted(schedule_request.jobs, key=lambda job: job.order)
            job_ids = [job.id for job in sorted_jobs]

        # DAG 업데이트 - description 제외
        result = airflow_service.update_dag(
            dag_id=schedule_id,
            name=schedule_request.title,
            # description 필드 제외 (Airflow API에서 읽기 전용)
            # description=schedule_request.description,
            cron_expression=cron_expression,
            job_ids=job_ids,
            start_date=schedule_request.start_date,
            end_date=schedule_request.end_date,
            success_emails=schedule_request.success_emails,
            failure_emails=schedule_request.failure_emails
        )

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedule_id": schedule_id,
                "updated_at": datetime.now().isoformat(),
                "message": "스케줄이 업데이트되었습니다."
            }
        })
    except Exception as e:
        print(f"Error updating schedule: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 업데이트에 실패했습니다: {str(e)}"
        })


def _convert_frequency_to_cron(frequency: str, execution_time: str, start_date: datetime) -> str:
    """
    사용자 친화적인 주기 표현을 cron 표현식으로 변환
    시작 날짜를 기준으로 weekly, monthly 주기 설정

    Args:
        frequency: 주기 표현 ("daily", "weekly", "monthly" 등)
        execution_time: "HH:MM" 형식의 실행 시간 (예: "09:30")
        start_date: 스케줄 시작 날짜
    """
    # 시간과 분 추출
    try:
        hour, minute = map(int, execution_time.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError("시간 형식이 잘못되었습니다. 형식은 'HH:MM'이어야 합니다.")
    except ValueError as e:
        raise ValueError(f"시간 형식이 잘못되었습니다. 형식은 'HH:MM'이어야 합니다. 상세: {str(e)}")

    # 이미 cron 표현식인 경우
    if frequency.count(" ") >= 4:
        return frequency

    if frequency == "daily":
        return f"{minute} {hour} * * *"
    elif frequency == "weekly":
        day_of_week = start_date.weekday()
        cron_day = (day_of_week + 1) % 7
        return f"{minute} {hour} * * {cron_day}"
    elif frequency == "monthly":
        # 시작 날짜의 일자에 실행
        day_of_month = start_date.day
        return f"{minute} {hour} {day_of_month} * *"
    elif frequency.startswith("every_"):
        # every_2_days, every_3_hours 등의 형식 처리
        parts = frequency.split("_")
        if len(parts) == 3:
            interval = int(parts[1])
            unit = parts[2]

            if unit == "hours":
                if interval >= 24:
                    # hours는 24 미만이어야 함
                    raise ValueError("시간 간격은 24 미만이어야 합니다. 하루 이상은 days를 사용하세요.")
                return f"{minute} */{interval} * * *"
            elif unit == "days":
                return f"{minute} {hour} */{interval} * *"
            elif unit == "weeks":
                # 주 단위로는 cron에서 직접 지원하지 않으므로 7*interval 일로 변환
                return f"{minute} {hour} */{7 * interval} * *"

    # 알 수 없는 형식이면 기본값 (매일 정해진 시간)
    return f"{minute} {hour} * * *"

@router.get("")
async def get_all_schedules(
        request: Request,
        status: Optional[str] = Query(None, description="Filter by status (active/paused)"),
        search: Optional[str] = Query(None, description="Search by title"),
        include_job_status: bool = Query(False, description="Include job status from recent run")
) -> JSONResponse:
    """
    모든 스케줄(DAG) 목록을 반환하는 API
    - 각 DAG의 상세 정보 포함
    - 상태별 필터링 (활성/비활성)
    - 제목 검색
    - 작업 상태 포함 여부 설정
    """
    try:
        # 서비스 함수 호출
        schedules = airflow_service.get_all_schedules_with_details(
            status=status,
            search=search,
            include_job_status=include_job_status
        )

        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedules": schedules,
                "total": len(schedules)
            }
        })
    except Exception as e:
        print(f"Error getting schedules: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"스케줄 목록 조회에 실패했습니다: {str(e)}"
        })