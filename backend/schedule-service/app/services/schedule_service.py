from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
from croniter import croniter

from app.core.config import settings
from app.core.log_config import logger
from app.services.airflow_client import airflow_client
from app.utils import date_utils, cron_utils, log_utils
from app.core import auth
from app.db.database import SessionLocal
from app.crud import schedule_crud
from app.models.schedule_models import ScheduleJob


class ScheduleService:
    """스케줄 조회 및 관리 서비스 클래스"""

    @staticmethod
    def get_schedule_detail(schedule_id: str, user_id: int = None, db=None) -> Dict[str, Any]:
        """스케줄(DAG) 상세 정보 조회와 관련 job 정보를 함께 반환"""
        close_db = False
        try:
            # DB 세션을 외부에서 받지 않았을 경우에만 새로 생성
            if db is None:
                db = SessionLocal()
                close_db = True

            # DAG 상세 정보 조회
            dag_detail = airflow_client.get_dag_detail(schedule_id)

            # 태그에서 title 추출
            title = ScheduleService.extract_title_from_tags(dag_detail.get("tags", []))
            if not title:
                title = dag_detail.get("dag_display_name", schedule_id)

            # DB에서 스케줄 정보 조회
            db_schedule = schedule_crud.get_schedule_by_dag_id(db, schedule_id)
            if db_schedule:
                # DB에 저장된 정보 사용
                title = db_schedule.title
                description = db_schedule.description
                start_date = db_schedule.start_date.isoformat() if db_schedule.start_date else None
                end_date = db_schedule.end_date.isoformat() if db_schedule.end_date else None
                success_emails = db_schedule.success_emails or []
                failure_emails = db_schedule.failure_emails or []

                # job_ids 가져오기
                schedule_jobs = db.query(ScheduleJob).filter(ScheduleJob.schedule_id == db_schedule.id).order_by(
                    ScheduleJob.order).all()
                job_ids = [job.job_id for job in schedule_jobs]
            else:
                # DB에 정보가 없는 경우 기본값 사용
                description = dag_detail.get("description", "")
                start_date = None
                end_date = None
                success_emails = []
                failure_emails = []
                job_ids = []

                # 태그에서 시작/종료일 추출 시도
                for tag in dag_detail.get("tags", []):
                    tag_name = tag.get("name") if isinstance(tag, dict) else tag
                    if tag_name and tag_name.startswith("start_date:"):
                        start_date = tag_name[11:]
                    elif tag_name and tag_name.startswith("end_date:"):
                        end_date = tag_name[9:]
                        end_date = None if end_date == "None" else end_date

            # job_ids가 있고 user_id가 제공된 경우 job 상세 정보 조회
            tasks = []
            if job_ids and user_id is not None:
                job_details = ScheduleService.get_job_commands(job_ids, user_id=user_id)

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
            schedule_interval = dag_detail.get("schedule_interval")
            if isinstance(schedule_interval, dict) and "__type" in schedule_interval:
                frequency_cron = schedule_interval.get("__type", "")
            else:
                frequency_cron = str(schedule_interval) if schedule_interval else ""

            # 주기 문자열로 변환 (역변환)
            frequency = cron_utils.convert_cron_to_frequency(frequency_cron)
            frequency_display = cron_utils.parse_cron_to_friendly_format(frequency_cron)

            # execution_time이 DB에 없으면 cron에서 추출
            execution_time = None
            if db_schedule and hasattr(db_schedule, 'execution_time'):
                execution_time = db_schedule.execution_time

            if not execution_time:
                execution_time = cron_utils.extract_execution_time_from_cron(frequency_cron)

            # 응답 데이터 구성
            schedule_data = {
                "schedule_id": schedule_id,
                "title": title,
                "description": description,
                "frequency": frequency,
                "frequency_cron": frequency_cron,
                "frequency_display": frequency_display,
                "is_paused": dag_detail.get("is_paused", False),
                "created_at": dag_detail.get("last_parsed_time", ""),
                "updated_at": db_schedule.updated_at.isoformat() if db_schedule and db_schedule.updated_at else None,
                "start_date": start_date,
                "end_date": end_date,
                "execution_time": execution_time,
                "success_emails": success_emails,
                "failure_emails": failure_emails,
                "jobs": tasks
            }

            return schedule_data

        except Exception as e:
            logger.error(f"Error getting schedule detail: {str(e)}")
            raise Exception(f"스케줄 상세 정보 조회에 실패했습니다: {str(e)}")
        finally:
            # 생성한 경우에만 세션 닫기
            if close_db and db is not None:
                db.close()

    @staticmethod
    def extract_title_from_tags(tags: List[Any]) -> Optional[str]:
        """태그 목록에서 title 태그를 찾아 반환합니다."""
        for tag in tags:
            tag_name = tag.get("name") if isinstance(tag, dict) else tag
            if tag_name and tag_name.startswith("title:"):
                return tag_name[6:]  # "title:" 부분을 제외한 실제 제목 반환
        return None

    @staticmethod
    def get_job_commands(job_ids: List[str], user_id: int = None) -> Dict[str, Any]:
        """주어진 job ID 리스트에 대한 상세 정보를 Job Service API를 통해 조회"""
        try:
            # Job Service URL 가져오기
            job_service_url = settings.JOB_SERVICE_URL
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

                job_details = {}
                for job_id in job_ids:
                    job_details[job_id] = None

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

    @staticmethod
    def get_schedule_run_detail_with_logs(schedule_id: str, run_id: str, user_id: int, db=None) -> Dict[str, Any]:
        """스케줄 실행 상세 정보와 작업별 에러 로그를 함께 조회"""
        close_db = False
        try:
            # DB 세션을 외부에서 받지 않았을 경우에만 새로 생성
            if db is None:
                db = SessionLocal()
                close_db = True

            # DAG 상세 정보 조회
            dag_detail = airflow_client.get_dag_detail(schedule_id)

            # 태그에서 title 추출 또는 dag_display_name 사용
            title = ScheduleService.extract_title_from_tags(dag_detail.get("tags", []))
            if not title:
                title = dag_detail.get("dag_display_name", schedule_id)

            # DB에서 title 확인
            db_schedule = schedule_crud.get_schedule_by_dag_id(db, schedule_id)
            if db_schedule:
                title = db_schedule.title

            # DAG 실행 상세 정보 조회
            run_detail = airflow_client.get_dag_run_detail(schedule_id, run_id)

            # 태스크 인스턴스 목록 조회
            task_instances = airflow_client.get_task_instances(schedule_id, run_id)

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
            job_details = ScheduleService.get_job_commands(job_ids, user_id)

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
                            task_logs = airflow_client.get_task_logs(schedule_id, run_id, task_id)

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
            schedule_data = ScheduleService.get_schedule_detail(schedule_id, user_id, db)

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
                "duration": date_utils.calculate_duration_seconds(
                    run_detail.get("start_date"),
                    run_detail.get("end_date")
                ),
                "jobs": list(jobs_data.values()),  # 딕셔너리를 리스트로 변환
                "summary": summary
            }

            return run_data
        except Exception as e:
            logger.error(f"Error getting schedule run detail: {str(e)}")
            raise e
        finally:
            # 생성한 경우에만 세션 닫기
            if close_db and db is not None:
                db.close()

    @staticmethod
    def get_all_schedules_with_details(user_id: int = None, db=None) -> Dict[str, Any]:
        """모든 스케줄(DAG) 목록을 상세 정보와 함께 반환"""
        close_db = False
        try:
            # DB 세션 생성
            if db is None:
                db = SessionLocal()
                close_db = True

            # 모든 DAG 목록 가져오기 (Airflow API)
            dags_response = airflow_client._get("dags", {"limit": 1000})
            dags = dags_response.get("dags", [])

            # DB에서 모든 스케줄 정보 가져오기 (N+1 쿼리 방지)
            db_schedules = {}
            schedule_job_map = {}
            try:
                # 모든 스케줄 정보를 한 번에 가져옴
                all_db_schedules = schedule_crud.get_all_schedules(db)
                for schedule in all_db_schedules:
                    db_schedules[schedule.dag_id] = schedule

                # 스케줄별 job_ids 가져오기 (N+1 쿼리 방지)
                for schedule_job in db.query(ScheduleJob).all():
                    if schedule_job.schedule_id not in schedule_job_map:
                        schedule_job_map[schedule_job.schedule_id] = []
                    schedule_job_map[schedule_job.schedule_id].append({
                        "job_id": schedule_job.job_id,
                        "order": schedule_job.order
                    })
            except Exception as e:
                logger.error(f"Error getting DB data: {str(e)}")

            schedule_list = []
            for dag in dags:
                dag_id = dag.get("dag_id")

                # Airflow API에서 기본 정보 구성
                schedule_data = {
                    "schedule_id": dag_id,
                    "title": dag.get("dag_display_name", dag_id),
                    "description": dag.get("description", ""),
                    "is_paused": dag.get("is_paused", False),
                    "owner": dag.get("owners", ["unknown"])[0] if dag.get("owners") else "unknown",
                    "jobs": [],
                    "last_run": None,
                    "next_run": None,
                    "success_emails": [],
                    "failure_emails": []
                }

                # 태그에서 title 추출 (fallback)
                title_from_tag = ScheduleService.extract_title_from_tags(dag.get("tags", []))
                if title_from_tag:
                    schedule_data["title"] = title_from_tag

                # 크론 표현식 및 주기 처리
                schedule_interval = dag.get("schedule_interval")
                cron_expr = ""
                if isinstance(schedule_interval, dict) and "__type" in schedule_interval:
                    cron_expr = schedule_interval.get("__type", "")
                else:
                    cron_expr = str(schedule_interval) if schedule_interval else ""

                schedule_data["frequency_cron"] = cron_expr
                schedule_data["frequency"] = cron_utils.convert_cron_to_frequency(cron_expr)
                schedule_data["frequency_display"] = cron_utils.parse_cron_to_friendly_format(cron_expr)
                schedule_data["execution_time"] = cron_utils.extract_execution_time_from_cron(cron_expr)

                # DB에서 스케줄 정보 가져오기
                db_schedule = db_schedules.get(dag_id)
                if db_schedule:
                    # DB에 저장된 정보 사용
                    schedule_data["title"] = db_schedule.title
                    schedule_data["description"] = db_schedule.description
                    schedule_data["success_emails"] = db_schedule.success_emails or []
                    schedule_data["failure_emails"] = db_schedule.failure_emails or []

                    # 생성/수정 일자
                    if hasattr(db_schedule, 'created_at') and db_schedule.created_at:
                        schedule_data["created_at"] = db_schedule.created_at.isoformat()
                    else:
                        schedule_data["created_at"] = dag.get("last_parsed_time", "")

                    if hasattr(db_schedule, 'updated_at') and db_schedule.updated_at:
                        schedule_data["updated_at"] = db_schedule.updated_at.isoformat()

                    # 시작일/종료일
                    if hasattr(db_schedule, 'start_date') and db_schedule.start_date:
                        schedule_data["start_date"] = db_schedule.start_date.isoformat()
                    if hasattr(db_schedule, 'end_date') and db_schedule.end_date:
                        schedule_data["end_date"] = db_schedule.end_date.isoformat()

                    # schedule.id로 schedule_jobs 테이블에서 job_ids 가져오기
                    schedule_id = db_schedule.id
                    job_infos = []

                    # 미리 가져온 job 맵에서 job 정보 조회
                    if schedule_id in schedule_job_map:
                        job_infos = sorted(schedule_job_map[schedule_id], key=lambda x: x["order"])
                        job_ids = [job_info["job_id"] for job_info in job_infos]

                        # job_ids를 이용하여 Job Service API 호출 (user_id가 있는 경우)
                        if job_ids and user_id is not None:
                            job_details = ScheduleService.get_job_commands(job_ids, user_id)
                            jobs = []
                            for job_info in job_infos:
                                job_id = job_info["job_id"]
                                detail = job_details.get(job_id, {})
                                if detail:
                                    jobs.append({
                                        "id": job_id,
                                        "order": job_info["order"] + 1,  # 0-based to 1-based
                                        "title": detail.get("title", f"Job {job_id}"),
                                        "description": detail.get("description", ""),
                                        "commands": detail.get("commands", [])
                                    })
                            schedule_data["jobs"] = jobs
                else:
                    # DB에 정보가 없는 경우, 태그에서 시작/종료일 추출 시도
                    for tag in dag.get("tags", []):
                        tag_name = tag.get("name", "")
                        if tag_name.startswith("start_date:"):
                            schedule_data["start_date"] = tag_name[11:]
                        elif tag_name.startswith("end_date:"):
                            end_date = tag_name[9:]
                            schedule_data["end_date"] = None if end_date == "None" else end_date

                    # 생성 시간은 Airflow에서 가져옴
                    schedule_data["created_at"] = dag.get("last_parsed_time", "")

                # 최근 실행 정보 조회
                try:
                    recent_runs = airflow_client.get_dag_runs(dag_id, limit=1)
                    if recent_runs:
                        recent_run = recent_runs[0]
                        schedule_data["last_run"] = {
                            "run_id": recent_run.get("dag_run_id"),
                            "status": recent_run.get("state"),
                            "start_time": recent_run.get("start_date"),
                            "end_time": recent_run.get("end_date")
                        }
                except Exception as e:
                    logger.error(f"Error getting recent runs for {dag_id}: {str(e)}")

                # 다음 실행 예정 조회
                if dag.get("next_dagrun"):
                    schedule_data["next_run"] = {
                        "execution_date": dag.get("next_dagrun"),
                        "scheduled_time": dag.get("next_dagrun_data_interval_start"),
                        "data_interval_end": dag.get("next_dagrun_data_interval_end")
                    }
                else:
                    try:
                        next_run_info = airflow_client.get_next_dag_run(dag_id)
                        if next_run_info:
                            schedule_data["next_run"] = next_run_info
                    except Exception as e:
                        logger.error(f"Error getting next run for {dag_id}: {str(e)}")

                schedule_list.append(schedule_data)

            # 생성일 기준으로 정렬 (최신순)
            schedule_list.sort(
                key=lambda x: x.get("created_at", "0000-00-00T00:00:00"),
                reverse=True
            )

            return {
                "schedules": schedule_list,
                "total": len(schedule_list)
            }

        except Exception as e:
            logger.error(f"Error getting schedules from Airflow: {str(e)}")
            return {
                "schedules": [],
                "total": 0
            }
        finally:
            if close_db and db is not None:
                db.close()

    @staticmethod
    def get_dag_runs_by_date(dags: List[Dict[str, Any]], target_date: str, db=None) -> Dict[str, Any]:
        """특정 날짜의 DAG 실행 내역 + 실행 예정(PENDING) DAG 반환"""
        close_db = False
        result = {
            "date": target_date,
            "success": [],
            "failed": [],
            "pending": []
        }

        try:
            # DB 세션을 외부에서 받지 않았을 경우에만 새로 생성
            if db is None:
                db = SessionLocal()
                close_db = True

            # timezone을 일관되게 적용하기 위해 UTC 사용
            target_date_dt = date_utils.parse_date_string(target_date)
            if not target_date_dt:
                raise ValueError(f"Invalid date format: {target_date}")

            start_dt = target_date_dt.replace(hour=0, minute=0, second=0)
            end_dt = target_date_dt.replace(hour=23, minute=59, second=59)

            # 현재 시각 (UTC 기준)
            now = date_utils.get_now_utc()
            logger.debug(f"현재 시간(UTC): {now}, 대상 날짜: {target_date}, 시작: {start_dt}, 종료: {end_dt}")

            start = date_utils.format_date_for_airflow(start_dt)
            end = date_utils.format_date_for_airflow(end_dt)

            # 이미 처리된 DAG ID 추적 (프로세싱 용도)
            processed_dag_ids = set()
            # 대기 목록에 추가되면 안되는 DAG ID (이미 실제 실행 이력이 있는 경우)
            already_processed_for_pending = set()

            # 모든 DAG를 순회하며 처리
            for dag in dags:
                dag_id = dag.get("dag_id")
                owner = dag.get("owners", ["unknown"])[0] if dag.get("owners") else "unknown"

                # 이미 처리된 DAG는 건너뛰기
                if dag_id in processed_dag_ids:
                    continue
                processed_dag_ids.add(dag_id)

                # DB에서 title 가져오기
                title = dag.get("dag_display_name", dag_id)
                description = dag.get("description", "")

                db_schedule = schedule_crud.get_schedule_by_dag_id(db, dag_id)
                if db_schedule:
                    title = db_schedule.title
                    description = db_schedule.description
                else:
                    # DB에 정보가 없는 경우 태그에서 title 추출 시도
                    title_from_tag = ScheduleService.extract_title_from_tags(dag.get("tags", []))
                    if title_from_tag:
                        title = title_from_tag

                is_paused = dag.get("is_paused", False)

                # 비활성 DAG는 건너뛰기
                if is_paused:
                    continue

                # 실행 이력 확인
                try:
                    dag_runs = airflow_client.get_dag_runs(dag_id, start_date=start, end_date=end, limit=100)
                except Exception as e:
                    logger.debug(f"Error getting dag runs for {dag_id}: {e}")
                    dag_runs = []

                # 이미 pending으로 추가됐는지 확인하는 플래그
                already_added_as_pending = False

                # 실행 기록이 있는 경우 처리
                if dag_runs:
                    # DAG에 실행 이력이 있으면 대기 목록에 추가하지 않도록 표시
                    already_processed_for_pending.add(dag_id)

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
                            already_added_as_pending = True
                            logger.debug(f"DAG {dag_id} 기존 실행 상태로 pending 추가: {state}")

                # 미래 예정된 실행 확인 (이미 실행 이력이 있으면 추가하지 않음)
                if not already_added_as_pending and dag_id not in already_processed_for_pending:
                    # 시작일 추출 - DAG ID에서 날짜 부분 추출
                    dag_start_date = date_utils.extract_date_from_dag_id(dag_id)

                    # DB에서 시작일 가져오기 시도
                    if not dag_start_date and db_schedule and db_schedule.start_date:
                        dag_start_date = db_schedule.start_date

                    # 시작일이 대상 날짜 이전이거나 같은 경우, 또는 시작일을 확인할 수 없는 경우
                    valid_start_date = (dag_start_date is None) or (target_date_dt.date() >= dag_start_date.date())

                    if valid_start_date:
                        # 스케줄 정보 확인
                        schedule_interval = dag.get("schedule_interval")
                        cron_expr = ""
                        if isinstance(schedule_interval, dict) and "__type" in schedule_interval:
                            cron_expr = schedule_interval.get("__type", "")
                        else:
                            cron_expr = str(schedule_interval) if schedule_interval else ""

                        if cron_expr and croniter.is_valid(cron_expr):
                            try:
                                # 해당 날짜의 00:00:00을 기준으로 크론 표현식 평가
                                cron_iter = croniter(cron_expr, start_dt)
                                execution_time = cron_iter.get_next(datetime)

                                # 시간대 확인 및 추가
                                if execution_time.tzinfo is None:
                                    execution_time = execution_time.replace(tzinfo=timezone.utc)

                                logger.debug(
                                    f"DAG {dag_id} - 다음 실행: {execution_time}, 오늘?: {execution_time <= end_dt}, 미래?: {execution_time > now}")

                                # 같은 날짜 내에 실행 시간이 있고, 아직 실행 시간이 지나지 않았는지 확인
                                if execution_time <= end_dt and execution_time > now:
                                    next_run_time = execution_time.isoformat()
                                    logger.debug(f"DAG {dag_id} pending으로 추가: {next_run_time}")

                                    result["pending"].append({
                                        "schedule_id": dag_id,
                                        "title": title,
                                        "description": description,
                                        "owner": owner,
                                        "status": "pending",
                                        "next_run_time": next_run_time
                                    })
                            except Exception as e:
                                logger.debug(f"Error calculating execution time for {dag_id}: {str(e)}")

            # 결과 출력
            logger.debug(
                f"Final result for {target_date}: success={len(result['success'])}, failed={len(result['failed'])}, pending={len(result['pending'])}")
            logger.debug(f"Pending DAGs: {[item['schedule_id'] for item in result['pending']]}")
        finally:
            # 생성한 경우에만 세션 닫기
            if close_db and db is not None:
                db.close()

        # finally 블록 바깥에서 return
        return result

    @staticmethod
    def _get_schedules_from_db(db=None) -> List[Dict[str, Any]]:
        """DB에서 스케줄 기본 정보를 가져옵니다 (fallback용)"""
        close_db = False
        result = []  # 여기서 result를 초기화하여 함수 밖에서도 접근 가능하게 함
        try:
            if db is None:
                db = SessionLocal()
                close_db = True

            # DB에서 스케줄 정보 가져오기
            schedules = schedule_crud.get_all_schedules(db)

            # DB 객체를 딕셔너리로 변환
            for schedule in schedules:
                # Schedule 모델 객체를 딕셔너리로 변환
                schedule_dict = {
                    "schedule_id": schedule.dag_id,
                    "title": schedule.title,
                    "description": schedule.description,
                    "frequency": schedule.frequency,
                    "frequency_cron": schedule.frequency_cron,
                    "execution_time": schedule.execution_time,
                    "is_paused": schedule.is_paused,
                    "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
                    "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
                    "success_emails": schedule.success_emails or [],
                    "failure_emails": schedule.failure_emails or [],
                    "owner": schedule.owner,
                    "created_by": schedule.created_by,
                    "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
                    "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
                    "last_run": None,
                    "next_run": None,
                    "jobs": []
                }

                # job_ids 가져오기
                try:
                    schedule_jobs = []
                    if hasattr(schedule, 'jobs') and schedule.jobs:
                        # 순서에 따라 정렬
                        schedule_jobs = sorted(schedule.jobs, key=lambda x: x.order)
                        schedule_dict["job_ids"] = [job.job_id for job in schedule_jobs]
                    else:
                        # DB에서 별도 쿼리로 가져오기
                        schedule_jobs = db.query(ScheduleJob).filter(ScheduleJob.schedule_id == schedule.id).order_by(
                            ScheduleJob.order).all()
                        schedule_dict["job_ids"] = [job.job_id for job in schedule_jobs]
                except Exception as e:
                    logger.error(f"Error getting job_ids for schedule {schedule.dag_id}: {str(e)}")
                    schedule_dict["job_ids"] = []

                result.append(schedule_dict)
        finally:
            if close_db and db is not None:
                db.close()

        # finally 블록 바깥에서 return 문 사용
        return result