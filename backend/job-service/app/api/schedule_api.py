from typing import List, Optional
from fastapi import APIRouter, Request, Query, HTTPException
from starlette.responses import JSONResponse
from datetime import datetime
from app.schemas.schedule_schema import (
    ScheduleCreateRequest, 
    ScheduleUpdateRequest
)
from app.services import airflow_service

router = APIRouter(
    prefix="/api/schedules"
)

@router.post("")
async def create_schedule(request: Request, schedule_request: ScheduleCreateRequest) -> JSONResponse:
    # user_id = request.headers.get("x-user-id")
    user_id=1
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        # frequency를 cron 표현식으로 변환
        cron_expression = _convert_frequency_to_cron(
            schedule_request.frequency, 
            schedule_request.execution_time
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

@router.get("/calendar")
async def get_schedule_calendar(
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
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # DAG 실행에 포함된 태스크(job) 목록 조회
        tasks = []
        
        # 응답 데이터 구성
        schedule_data = {
            "schedule_id": schedule_id,
            "title": dag_detail.get("name", schedule_id),
            "description": dag_detail.get("description", ""),
            "frequency": dag_detail.get("schedule_interval", ""),
            "is_paused": dag_detail.get("is_paused", False),
            "created_at": dag_detail.get("created_at", datetime.now().isoformat()),
            "updated_at": dag_detail.get("updated_at", None),
            "jobs": tasks  # 태스크 목록 추가
        }
        
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
    # user_id = request.headers.get("x-user-id")
    user_id=1
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

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



@router.get("/date/{date}")
async def get_schedule_executions_by_date(
    request: Request,
    date: str  # 'YYYY-MM-DD' 형식
) -> JSONResponse:
    try:
        # 날짜 유효성 검사
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return JSONResponse(status_code=400, content={
                "result": "error",
                "message": "잘못된 날짜 형식입니다. 'YYYY-MM-DD' 형식으로 입력해주세요."
            })

        dags = airflow_service.get_all_dags()
        executions = airflow_service.get_dag_runs_by_date(dags, date)

        return JSONResponse(content={
            "result": "success",
            "data": executions
        })

    except Exception as e:
        print(f"Error getting schedule executions by date: {str(e)}")
        return JSONResponse(status_code=500, content={
            "result": "error",
            "message": f"날짜별 스케줄 실행 결과 조회에 실패했습니다: {str(e)}"
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
    # user_id = request.headers.get("x-user-id")
    user_id=1
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")
        
        if owner != dag_owner and owner not in dag_detail.get("tags", []):
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
                "schedule_name": dag_detail.get("name", schedule_id),
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
    # user_id = request.headers.get("x-user-id")
    user_id=1
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")
        
        if owner != dag_owner and owner not in dag_detail.get("tags", []):
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
                "logs_url": f"{airflow_service.settings.AIRFLOW_API_BASE_URL}/dags/{schedule_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs"
            })
        
        # 응답 데이터 구성
        run_data = {
            "schedule_id": schedule_id,
            "schedule_name": dag_detail.get("name", schedule_id),
            "run_id": run_id,
            "status": run_detail.get("state"),
            "start_time": run_detail.get("start_date"),
            "end_time": run_detail.get("end_date"),
            "duration": (
                datetime.fromisoformat(run_detail.get("end_date").replace("Z", "+00:00")) - 
                datetime.fromisoformat(run_detail.get("start_date").replace("Z", "+00:00"))
            ).total_seconds() if run_detail.get("end_date") and run_detail.get("start_date") else None,
            "conf": run_detail.get("conf", {}),
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

@router.post("/{schedule_id}/execute")
async def execute_schedule(request: Request, schedule_id: str) -> JSONResponse:
    # user_id = request.headers.get("x-user-id")
    user_id=1
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")
        
        if owner != dag_owner and owner not in dag_detail.get("tags", []):
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
    # user_id = request.headers.get("x-user-id")
    user_id=1
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")
        
        if owner != dag_owner and owner not in dag_detail.get("tags", []):
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

@router.put("/{schedule_id}")
async def update_schedule(
    request: Request,
    schedule_id: str,
    schedule_request: ScheduleUpdateRequest
) -> JSONResponse:
    # user_id = request.headers.get("x-user-id")
    user_id=1
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        # DAG 상세 정보 조회
        dag_detail = airflow_service.get_dag_detail(schedule_id)
        
        # 소유자 확인
        owner = f"user_{user_id}"
        dag_owner = dag_detail.get("owner", "")
        
        if owner != dag_owner and owner not in dag_detail.get("tags", []):
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
        
        # DAG 업데이트
        result = airflow_service.update_dag(
            dag_id=schedule_id,
            name=schedule_request.title,
            description=schedule_request.description,
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

def _convert_frequency_to_cron(frequency: str, execution_time: datetime) -> str:
    """
    사용자 친화적인 주기 표현을 cron 표현식으로 변환
    """
    hour = execution_time.hour
    minute = execution_time.minute
    
    # 이미 cron 표현식인 경우
    if frequency.count(" ") >= 4:  # 간단한 cron 표현식 체크 (최소 5개 필드)
        return frequency
    
    # 일반적인 표현을 cron으로 변환
    if frequency == "daily":
        return f"{minute} {hour} * * *"
    elif frequency == "weekly":
        # 월요일(1)에 실행
        return f"{minute} {hour} * * 1"
    elif frequency == "monthly":
        # 매월 1일에 실행
        return f"{minute} {hour} 1 * *"
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
                return f"{minute} {hour} */{7*interval} * *"
            
    # 알 수 없는 형식이면 기본값 (매일 정해진 시간)
    return f"{minute} {hour} * * *"