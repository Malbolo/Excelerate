from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from croniter import croniter
import os

from app.core.config import settings
from app.core.log_config import logger
# from app.db.database import get_db
# 모듈 단위 import로 변경
from app.services import dag_query
from app.services.metadata import get_dag_metadata
from app.services.utils import cron, log_utils, time
from app.core import auth

def get_schedule_detail(schedule_id: str, user_id: int = None) -> Dict[str, Any]:
    """스케줄(DAG) 상세 정보 조회와 관련 job 정보를 함께 반환"""
    try:
        # DAG 상세 정보 조회
        dag_detail = dag_query.get_dag_detail(schedule_id)

        title = extract_title_from_tags(dag_detail.get("tags", []))

        # 메타데이터에서 추가 정보 조회
        metadata = get_dag_metadata(schedule_id)

        # job 정보 조회 (Job Service API 호출)
        job_ids = metadata.get("job_ids", [])

        # user_id 전달하여 job의 상세 정보 조회 (commands 포함)
        job_details = get_job_details(job_ids, user_id=user_id)

        # 작업 목록을 순서대로 구성
        tasks = []
        for idx, job_id in enumerate(job_ids):
            job_info = job_details.get(job_id, {})

            task = {
                "id": job_id,
                "order": idx + 1,
                "title": job_info.get("title", f"Job {job_id}"),
                "description": job_info.get("description", ""),
                "commands": job_info.get("commands", [])
            }

            tasks.append(task)

        # 크론 표현식 처리
        frequency_cron = ""
        if "schedule_interval" in dag_detail:
            schedule_interval = dag_detail.get("schedule_interval")
            if isinstance(schedule_interval, dict) and "__type" in schedule_interval:
                frequency_cron = schedule_interval.get("value", "")
            else:
                frequency_cron = schedule_interval

        # 주기 문자열로 변환 (역변환)
        frequency = cron.convert_cron_to_frequency(frequency_cron)
        frequency_display = cron.parse_cron_to_friendly_format(frequency_cron)
        # execution_time이 메타데이터에 없으면 cron에서 추출
        execution_time = metadata.get("execution_time")
        if not execution_time:
            execution_time = cron.extract_execution_time_from_cron(dag_detail.get("schedule_interval"))

        # 응답 데이터 구성
        schedule_data = {
            "schedule_id": schedule_id,
            "title": title,
            "description": dag_detail.get("description", ""),
            "frequency": frequency,
            "frequency_cron": frequency_cron,
            "frequency_display": frequency_display,
            "is_paused": dag_detail.get("is_paused", False),
            "created_at": dag_detail.get("created_at", datetime.now().isoformat()),
            "updated_at": dag_detail.get("updated_at", None),
            "start_date": metadata.get("start_date"),
            "end_date": metadata.get("end_date"),
            "execution_time": execution_time,
            "success_emails": metadata.get("success_emails", []),
            "failure_emails": metadata.get("failure_emails", []),
            "jobs": tasks
        }

        return schedule_data

    except Exception as e:
        logger.error(f"Error getting schedule detail: {str(e)}")
        raise Exception(f"스케줄 상세 정보 조회에 실패했습니다: {str(e)}")

def extract_title_from_tags(tags: List[dict]) -> Optional[str]:
    """태그 목록에서 title 태그를 찾아 반환합니다."""
    for tag in tags:
        tag_name = tag.get("name") if isinstance(tag, dict) else tag
        if tag_name and tag_name.startswith("title:"):
            return tag_name[6:]  # "title:" 부분을 제외한 실제 제목 반환
    return None

def get_job_details(job_ids: List[str], user_id: int = None) -> Dict[str, Any]:
    """주어진 job ID 리스트에 대한 상세 정보를 Job Service API를 통해 조회"""
    try:
        job_details = {}

        # Job Service URL 가져오기
        job_service_url = os.getenv("JOB_SERVICE_URL")
        if not job_service_url:
            raise Exception("JOB_SERVICE_URL 환경 변수가 설정되지 않았습니다.")

        try:
            # 요청 형식 - 단순히 job_ids 리스트 전달
            response = auth.call_service_api(
                service_url=job_service_url,
                method="POST",
                endpoint="/api/jobs/for-schedule/commands",
                data={"job_ids": job_ids},
                user_id=user_id
            )

            # 응답 형식에 맞게 처리
            if response and "jobs" in response:
                # 배열을 딕셔너리로 변환
                for job in response["jobs"]:
                    job_id = job.get("id")
                    if job_id:
                        if "commands" not in job or not isinstance(job["commands"], list):
                            job["commands"] = []
                        job_details[job_id] = job
            else:
                logger.warning("Job Service API 응답에 'jobs' 필드가 없습니다.")

        except Exception as e:
            logger.error(f"Job Service API 호출 중 오류 발생: {str(e)}")
            # API 호출 실패 시 최소한의 정보만 포함
            for job_id in job_ids:
                job_details[job_id] = {
                    "id": job_id,
                    "title": f"Job {job_id}",
                    "description": "API 호출 실패",
                    "commands": []
                }

        return job_details

    except Exception as e:
        logger.error(f"Job 상세 정보 조회 중 오류 발생: {str(e)}")
        # 오류 발생 시 빈 정보 반환
        empty_details = {}
        for job_id in job_ids:
            empty_details[job_id] = {
                "id": job_id,
                "title": f"Job {job_id}",
                "description": "오류 발생",
                "commands": []
            }
        return empty_details

def get_schedule_run_detail_with_logs(schedule_id: str, run_id: str, user_id: int) -> Dict[str, Any]:
    """스케줄 실행 상세 정보와 작업별 에러 로그를 함께 조회"""
    try:
        # DAG 상세 정보 조회
        dag_detail = dag_query.get_dag_detail(schedule_id)

        # 태그에서 title 추출
        title = extract_title_from_tags(dag_detail.get("tags", []))
        if not title:
            title = dag_detail.get("name", schedule_id)

        # DAG 실행 상세 정보 조회
        run_detail = dag_query.get_dag_run_detail(schedule_id, run_id)

        # 태스크 인스턴스 목록 조회
        task_instances = dag_query.get_task_instances(schedule_id, run_id)

        # job_id 목록 추출
        job_ids = []
        for task in task_instances:
            task_id = task.get("task_id", "")
            if task_id.startswith("job_"):
                try:
                    job_id = task_id.split("_")[1]
                    job_ids.append(job_id)
                except (IndexError, ValueError):
                    pass

        # job 상세 정보 조회
        job_details = get_job_details(job_ids, user_id)

        # 태스크 데이터 구성 (job_id를 키로 사용)
        jobs_data = {}
        successful_jobs = 0
        failed_jobs = 0
        pending_jobs = 0

        for task in task_instances:
            task_id = task.get("task_id", "")

            # job_id 추출
            if task_id.startswith("job_"):
                try:
                    job_id = task_id.split("_")[1]

                    # job 정보 가져오기
                    job_info = job_details.get(job_id, {})

                    # 작업 상태 확인
                    status = task.get("state")
                    if status == "success":
                        successful_jobs += 1
                    elif status in ["failed", "upstream_failed"]:
                        failed_jobs += 1
                    else:  # 'running', 'queued', 등
                        pending_jobs += 1

                    # 에러 로그 가져오기 (실패한 작업만)
                    error_log = None
                    if status in ["failed", "upstream_failed"]:
                        # Airflow API에서 로그 가져오기
                        task_logs = dag_query.get_task_logs(schedule_id, run_id, task_id)

                        if task_logs:
                            # 에러 메시지 및 스택 트레이스 추출
                            error_message = log_utils.extract_error_message(task_logs)
                            error_trace = log_utils.extract_error_trace(task_logs)

                            error_log = {
                                "error_message": error_message,
                                "error_trace": error_trace,
                                "error_time": task.get("end_date"),
                                "error_code": f"TASK_ERROR_{job_id}"
                            }

                    # 작업 상태 및 실행 정보
                    job_data = {
                        "id": job_id,
                        "title": job_info.get("title", f"Job {job_id}"),
                        "description": job_info.get("description", ""),
                        "commands": job_info.get("commands", []),
                        "status": status,
                        "start_time": task.get("start_date"),
                        "end_time": task.get("end_date"),
                        "duration": task.get("duration"),
                        "logs_url": f"{settings.AIRFLOW_API_URL}/dags/{schedule_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs",
                        "error_log": error_log
                    }

                    jobs_data[job_id] = job_data
                except (IndexError, ValueError):
                    pass

        # 스케줄 정보 조회 (description 포함)
        schedule_data = get_schedule_detail(schedule_id, user_id)

        # 작업 요약 정보 구성
        summary = {
            "total_jobs": len(jobs_data),
            "successful_jobs": successful_jobs,
            "failed_jobs": failed_jobs,
            "pending_jobs": pending_jobs
        }

        # 응답 데이터 구성
        run_data = {
            "schedule_id": schedule_id,
            "title": title,
            "description": schedule_data.get("description", ""),
            "run_id": run_id,
            "status": run_detail.get("state"),
            "start_time": run_detail.get("start_date"),
            "end_time": run_detail.get("end_date"),
            "duration": time.calculate_duration_seconds(run_detail.get("start_date"), run_detail.get("end_date")),
            "jobs": list(jobs_data.values()),  # 딕셔너리를 리스트로 변환
            "summary": summary
        }

        return run_data
    except Exception as e:
        logger.error(f"Error getting schedule run detail: {str(e)}")
        raise e


def get_all_schedules_with_details(
        status: Optional[str] = None,
        search: Optional[str] = None,
        include_job_status: bool = False,
        user_id: int = None
) -> List[Dict[str, Any]]:
    """모든 스케줄(DAG) 목록을 상세 정보와 함께 반환"""
    # 모든 DAG 기본 정보 조회
    dags = dag_query.get_all_dags(limit=1000)

    # 상태별 필터링
    if status:
        if status.lower() == "active":
            dags = [dag for dag in dags if not dag.get("is_paused", False)]
        elif status.lower() == "paused":
            dags = [dag for dag in dags if dag.get("is_paused", False)]

    # 제목 검색
    if search:
        search = search.lower()
        filtered_dags = []
        for dag in dags:
            # 태그에서 title 추출
            dag_title = extract_title_from_tags(dag.get("tags", []))
            if not dag_title:
                dag_title = dag.get("name", dag.get("dag_id", ""))

            # 검색어가 dag_id, title, description에 포함되어 있는지 확인
            if (search in dag.get("dag_id", "").lower() or
                    search in dag_title.lower() or
                    search in dag.get("description", "").lower()):
                filtered_dags.append(dag)
        dags = filtered_dags

    # 각 DAG의 상세 정보 조회
    schedule_list = []
    # db = next(get_db())
    try:
        for dag in dags:
            dag_id = dag.get("dag_id", "")
            owner = dag.get("owners", ["unknown"])[0]
            # 태그에서 title 추출
            title = extract_title_from_tags(dag.get("tags", []))
            if not title:
                title = dag.get("name", dag_id)

            try:
                # 상세 정보 조회
                schedule_data = get_schedule_detail(dag_id, user_id)

                # 기본적으로 마지막 실행과 다음 실행 정보를 초기화
                schedule_data["last_run"] = None
                schedule_data["next_run"] = None

                # 최근 실행 정보 조회 (마지막 실행 정보를 위해)
                recent_runs = dag_query.get_dag_runs(dag_id, limit=1)

                if recent_runs:
                    recent_run = recent_runs[0]
                    run_id = recent_run.get("dag_run_id")

                    # 마지막 실행 정보 설정
                    schedule_data["last_run"] = {
                        "run_id": run_id,
                        "status": recent_run.get("state"),
                        "start_time": recent_run.get("start_date"),
                        "end_time": recent_run.get("end_date")
                    }

                    schedule_data["owner"] = owner
                    # 작업 상태 포함 여부에 따라 작업 상태 정보 추가
                    if include_job_status:
                        # 작업 실행 상태 조회
                        task_instances = dag_query.get_task_instances(dag_id, run_id)

                        # 작업 정보에 상태 추가
                        tasks_with_status = []
                        for job in schedule_data.get("jobs", []):
                            job_id = job.get("id")
                            # 해당 job_id와 일치하는 태스크 인스턴스 찾기
                            matching_task = None
                            for task in task_instances:
                                task_id = task.get("task_id", "")
                                if task_id == f"job_{job_id}":
                                    matching_task = task
                                    break

                            # 작업 정보에 상태 추가
                            job_with_status = job.copy()
                            if matching_task:
                                job_with_status["status"] = matching_task.get("state", "unknown")
                                job_with_status["start_time"] = matching_task.get("start_date")
                                job_with_status["end_time"] = matching_task.get("end_date")
                                job_with_status["duration"] = matching_task.get("duration")
                            else:
                                job_with_status["status"] = "not_run"

                            tasks_with_status.append(job_with_status)

                        # 원래 jobs 배열 교체
                        schedule_data["jobs"] = tasks_with_status

                # 다음 실행 예정 정보 조회
                next_run_info = dag_query.get_next_dag_run(dag_id)
                if next_run_info:
                    schedule_data["next_run"] = next_run_info

                schedule_list.append(schedule_data)
            except Exception as detail_err:
                logger.error(f"Error getting detail for {dag_id}: {str(detail_err)}")
                # 오류 시 기본 정보만 추가
                schedule_list.append({
                    "schedule_id": dag_id,
                    "title": title,
                    "description": dag.get("description", ""),
                    "is_paused": dag.get("is_paused", False),
                    "frequency": "unknown",
                    "jobs": [],
                    "last_run": None,
                    "next_run": None,
                    "owner": owner,
                })
    finally:
        logger.debug(f"schedule_list: {schedule_list}")
        # db.close()

    schedule_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return schedule_list

def get_dag_runs_by_date(dags: List[Dict[str, Any]], target_date: str) -> Dict[str, Any]:
    """특정 날짜의 DAG 실행 내역 + 실행 예정(PENDING) DAG 반환"""
    # timezone을 일관되게 적용하기 위해 UTC 사용
    target_date_dt = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    start_dt = target_date_dt.replace(hour=0, minute=0, second=0)
    end_dt = target_date_dt.replace(hour=23, minute=59, second=59)

    # 현재 시각 (UTC 기준)
    now = datetime.now(timezone.utc)

    start = start_dt.isoformat()
    end = end_dt.isoformat()

    result = {
        "date": target_date,
        "success": [],
        "failed": [],
        "pending": []
    }

    logger.debug(f"Processing dags for date: {target_date}, dags count: {len(dags)}")

    # 대상 날짜의 문자열 형식 (YYYY-MM-DD)
    target_date_str = target_date_dt.strftime("%Y-%m-%d")

    # 모든 DAG를 순회하며 처리
    for dag in dags:
        dag_id = dag.get("dag_id")
        owner = dag.get("owners", ["unknown"])[0]

        # 태그에서 title 추출
        title = extract_title_from_tags(dag.get("tags", []))
        if not title:
            title = dag.get("name", dag_id)  # 태그에 없으면 name이나 dag_id 사용

        description = dag.get("description", "")
        is_paused = dag.get("is_paused", False)

        # 비활성 DAG는 건너뛰기
        if is_paused:
            continue

        # 실행 이력 확인
        try:
            dag_runs = dag_query.get_dag_runs(dag_id, start_date=start, end_date=end, limit=100)
        except Exception as e:
            logger.debug(f"Error getting dag runs for {dag_id}: {e}")
            dag_runs = []

        if dag_runs:
            # 실행 기록이 있는 경우, 성공/실패에 따라 분류
            for run in dag_runs:
                state = run.get("state", "").lower()
                run_info = {
                    "schedule_id": dag_id,
                    "run_id": run.get("dag_run_id"),
                    "title": title,
                    "description": description,
                    "owner": owner,
                    "status": state,
                    "start_time": run.get("start_date"),
                    "end_time": run.get("end_date")
                }

                if state == "success":
                    result["success"].append(run_info)
                elif state in ("failed", "error"):
                    result["failed"].append(run_info)
                else:
                    # "running", "queued" 등의 상태는 pending으로 표시
                    result["pending"].append(run_info)
        else:
            # 실행 이력이 없는 경우, 시작일 및 실행 시각 확인
            should_be_pending = False
            next_run_time = None

            # 시작일 추출 - DAG ID에서 날짜 부분 추출
            dag_start_date = _extract_date_from_dag_id(dag_id)

            # 시작일이 대상 날짜 이전이거나 같은 경우에만 계속 진행
            if (dag_start_date and target_date_dt >= dag_start_date) or dag_start_date is None:
                # 스케줄 정보 확인
                schedule_interval = dag.get("schedule_interval", "")
                if isinstance(schedule_interval, dict) and "value" in schedule_interval:
                    schedule_interval = schedule_interval["value"]

                if schedule_interval and croniter.is_valid(schedule_interval):
                    try:
                        # 해당 날짜의 00:00:00을 기준으로 크론 표현식 평가
                        cron_iter = croniter(schedule_interval, start_dt)
                        execution_time = cron_iter.get_next(datetime)

                        # 같은 날짜 내에 실행 시간이 있고, 아직 실행 시간이 지나지 않았는지 확인
                        if execution_time <= end_dt and execution_time > now:
                            should_be_pending = True
                            next_run_time = execution_time.isoformat()
                            logger.debug(f"{dag_id} will run at {next_run_time} on {target_date}")
                    except Exception as e:
                        logger.debug(f"Error calculating execution time for {dag_id}: {str(e)}")

            if should_be_pending:
                result["pending"].append({
                    "schedule_id": dag_id,
                    "title": title,
                    "description": description,
                    "owner": owner,
                    "status": "pending",
                    "next_run_time": next_run_time
                })

    # 결과 출력
    logger.debug(
        f"Final result for {target_date}: success={len(result['success'])}, failed={len(result['failed'])}, pending={len(result['pending'])}")

    return result

def _extract_date_from_dag_id(dag_id: str) -> datetime:
    """DAG ID에서 날짜 추출 - userid_time 형식에 맞게 수정"""
    try:
        # DAG ID 형식: 'owner_YYYYMMDDHHMMSS' 또는 'owner_YYYYMMDDHHMMSS[f]'
        parts = dag_id.split('_')
        if len(parts) >= 2:
            # 두 번째 부분이 날짜 형식인지 확인
            date_part = parts[1]

            # 날짜 부분이 숫자로 시작하는지 확인 (밀리초 부분 처리)
            if date_part and date_part[:8].isdigit():
                year_part = int(date_part[:4])
                month_part = int(date_part[4:6])
                day_part = int(date_part[6:8])

                # 유효한 날짜인지 확인
                if 2000 <= year_part <= 2100 and 1 <= month_part <= 12 and 1 <= day_part <= 31:
                    # 시간 부분이 있으면 시간도 설정 (선택적)
                    if len(date_part) >= 14 and date_part[8:14].isdigit():
                        hour_part = int(date_part[8:10])
                        minute_part = int(date_part[10:12])
                        second_part = int(date_part[12:14])
                        return datetime(year_part, month_part, day_part,
                                        hour_part, minute_part, second_part,
                                        tzinfo=timezone.utc)
                    else:
                        return datetime(year_part, month_part, day_part, tzinfo=timezone.utc)
    except (ValueError, IndexError) as e:
        logger.debug(f"Error extracting date from DAG ID {dag_id}: {str(e)}")
    return None