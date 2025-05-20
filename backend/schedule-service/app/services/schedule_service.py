from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
from croniter import croniter
import json

from app.core.config import settings
from app.core.log_config import logger
from app.services.airflow_client import airflow_client
from app.utils import date_utils, cron_utils, log_utils
from app.core import auth


# DB 관련 import 제거
# from app.db.database import SessionLocal
# from app.crud import schedule_crud
# from app.models.schedule_models import ScheduleJob


class ScheduleService:
    """스케줄 조회 및 관리 서비스 클래스"""

    @staticmethod
    def get_schedule_detail(schedule_id: str, user_id: int = None) -> Dict[str, Any]:
        """스케줄(DAG) 상세 정보 조회와 관련 job 정보를 함께 반환"""
        try:
            # DAG 상세 정보 조회
            dag_detail = airflow_client.get_dag_detail(schedule_id)

            # 태그 파싱
            parsed_tags = ScheduleService._parse_dag_tags(dag_detail.get("tags", []))

            # 태그에서 메타데이터 추출
            title = parsed_tags.get("title") or dag_detail.get("dag_display_name", schedule_id)
            description = parsed_tags.get("description") or dag_detail.get("description", "")
            start_date = parsed_tags.get("start_date")
            end_date = parsed_tags.get("end_date")
            end_date = None if end_date == "None" else end_date

            # 이메일 설정 추출
            success_emails_str = parsed_tags.get("success_emails", "")
            failure_emails_str = parsed_tags.get("failure_emails", "")

            success_emails = success_emails_str.split(",") if success_emails_str else []
            failure_emails = failure_emails_str.split(",") if failure_emails_str else []

            # job_ids 추출
            job_ids = []
            jobs_json = parsed_tags.get("jobs")
            if jobs_json:
                try:
                    jobs_data = json.loads(jobs_json)
                    job_ids = [job["job_id"] for job in sorted(jobs_data, key=lambda x: x["order"])]
                except:
                    logger.error(f"Error parsing jobs JSON from tags: {jobs_json}")

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
                cron_expression = schedule_interval.get("__type", "")
            else:
                cron_expression = str(schedule_interval) if schedule_interval else ""

            # 주기 문자열로 변환 (역변환)
            frequency = parsed_tags.get("frequency") or cron_utils.convert_cron_to_frequency(cron_expression)
            frequency_display = cron_utils.parse_cron_to_friendly_format(cron_expression)

            # execution_time 태그에서 추출
            execution_time = parsed_tags.get("execution_time")

            if not execution_time:
                execution_time = cron_utils.extract_execution_time_from_cron(cron_expression)

            # 응답 데이터 구성
            schedule_data = {
                "schedule_id": schedule_id,
                "title": title,
                "description": description,
                "frequency": frequency,
                "frequency_cron": cron_expression,
                "frequency_display": frequency_display,
                "is_paused": dag_detail.get("is_paused", False),
                "created_at": parsed_tags.get("created_at") or dag_detail.get("last_parsed_time", ""),
                "updated_at": parsed_tags.get("updated_at"),
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

    @staticmethod
    def _parse_dag_tags(tags: List[Dict[str, str]]) -> Dict[str, str]:
        """DAG 태그에서 메타데이터 추출 - 객체 형식의 태그만 처리"""
        parsed_tags = {}
        for tag in tags:
            # 객체 형식의 태그 처리 ({"name": "key:value"})
            if isinstance(tag, dict) and "name" in tag:
                tag_value = tag["name"]
                if isinstance(tag_value, str) and ":" in tag_value:
                    key, value = tag_value.split(":", 1)
                    parsed_tags[key] = value

        return parsed_tags

    @staticmethod
    def extract_title_from_tags(tags: List[str]) -> Optional[str]:
        """태그 목록에서 title 태그를 찾아 반환합니다. - 문자열 태그만 가정"""
        for tag in tags:
            if isinstance(tag, str) and tag.startswith("title:"):
                return tag[6:]  # "title:" 부분을 제외한 실제 제목 반환
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
                if (response and "result" in response and
                        response["result"] == "success" and "data" in response and "jobs" in response["data"]):
                    # 배열을 딕셔너리로 변환
                    for job in response["data"]["jobs"]:
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
    def get_schedule_run_detail_with_logs(schedule_id: str, run_id: str, user_id: int) -> Dict[str, Any]:
        """스케줄 실행 상세 정보와 작업별 에러 로그를 함께 조회"""
        try:
            # DAG 상세 정보 조회
            dag_detail = airflow_client.get_dag_detail(schedule_id)

            # 태그에서 메타데이터 추출
            parsed_tags = ScheduleService._parse_dag_tags(dag_detail.get("tags", []))

            # 태그에서 title 추출 또는 dag_display_name 사용
            title = parsed_tags.get("title") or dag_detail.get("dag_display_name", schedule_id)
            description = parsed_tags.get("description") or dag_detail.get("description", "")

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
            schedule_data = ScheduleService.get_schedule_detail(schedule_id, user_id)

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

    @staticmethod
    def get_dag_runs_by_date(dags: List[Dict[str, Any]], target_date: str) -> Dict[str, Any]:
        """특정 날짜의 DAG 실행 내역 + 실행 예정(PENDING) DAG 반환"""
        result = {
            "date": target_date,
            "success": [],
            "failed": [],
            "pending": []
        }

        try:
            # 날짜 변환 및 범위 설정
            target_date_dt = date_utils.parse_date_string(target_date)
            if not target_date_dt:
                raise ValueError(f"Invalid date format: {target_date}")

            # timezone 확인 및 추가
            if target_date_dt.tzinfo is None:
                target_date_dt = target_date_dt.replace(tzinfo=timezone.utc)

            day_start = target_date_dt.replace(hour=0, minute=0, second=0)
            day_end = target_date_dt.replace(hour=23, minute=59, second=59)

            # API 호출용 날짜 포맷
            start = date_utils.format_date_for_airflow(day_start)
            end = date_utils.format_date_for_airflow(day_end)

            # 현재 시각
            now = date_utils.get_now_utc()
            # timezone 확인
            if now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)

            # 이미 처리된 DAG 추적
            processed_dag_ids = set()
            already_processed_for_pending = set()

            # 모든 DAG 처리
            for dag in dags:
                dag_id = dag.get("dag_id")

                # 이미 처리됐거나 비활성 상태면 스킵
                if dag_id in processed_dag_ids or dag.get("is_paused", False):
                    continue

                processed_dag_ids.add(dag_id)

                # 태그에서 메타데이터 추출
                parsed_tags = ScheduleService._parse_dag_tags(dag.get("tags", []))

                # 기본 정보
                title = parsed_tags.get("title") or dag.get("dag_display_name", dag_id)
                description = parsed_tags.get("description") or dag.get("description", "")
                owner = parsed_tags.get("owner") or (
                    dag.get("owners", ["unknown"])[0] if dag.get("owners") else "unknown")

                # 실행 이력 확인
                already_added_as_pending = False
                try:
                    dag_runs = airflow_client.get_dag_runs(dag_id, start_date=start, end_date=end, limit=100)

                    # 실행 기록이 있는 경우
                    if dag_runs:
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
                                result["pending"].append(run_info)
                                already_added_as_pending = True

                except Exception as e:
                    logger.error(f"Error getting runs for {dag_id}: {str(e)}")
                    continue

                # 예정된 실행 확인 (실행 이력이 없고 대기 목록에 추가되지 않은 경우)
                if not already_added_as_pending and dag_id not in already_processed_for_pending:
                    # 시작일/종료일 추출
                    dag_start_date_str = parsed_tags.get('start_date')
                    dag_end_date_str = parsed_tags.get('end_date')

                    dag_start_date = None
                    dag_end_date = None

                    # 시작일 파싱
                    if dag_start_date_str:
                        try:
                            if '-' in dag_start_date_str:
                                year, month, day = map(int, dag_start_date_str.split('-'))
                                dag_start_date = datetime(year, month, day, tzinfo=timezone.utc)
                        except Exception as e:
                            logger.debug(f"Could not parse start_date for DAG {dag_id}: {str(e)}")

                    # 종료일 파싱
                    if dag_end_date_str and dag_end_date_str.lower() != 'none':
                        try:
                            if '-' in dag_end_date_str:
                                year, month, day = map(int, dag_end_date_str.split('-'))
                                dag_end_date = datetime(year, month, day, tzinfo=timezone.utc)
                        except Exception as e:
                            logger.debug(f"Could not parse end_date for DAG {dag_id}: {str(e)}")

                    # 날짜 범위 체크
                    if (dag_start_date and dag_start_date > day_end) or (dag_end_date and dag_end_date < day_start):
                        continue

                    # 크론 표현식 추출
                    cron_expr = parsed_tags.get("cron_expression")
                    if not cron_expr:
                        cron_expr = cron_utils.normalize_cron_expression(dag.get("schedule_interval"))

                    if cron_expr and croniter.is_valid(cron_expr):
                        try:
                            # 다음 실행 시간 계산
                            start_time = now if day_start <= now <= day_end else day_start
                            cron_iter = croniter(cron_expr, start_time)
                            execution_time = cron_iter.get_next(datetime)

                            # 시간대 추가
                            if execution_time.tzinfo is None:
                                execution_time = execution_time.replace(tzinfo=timezone.utc)

                            # 오늘 내에 실행 예정이고 현재 시간 이후인 경우
                            if execution_time <= day_end and execution_time > now:
                                result["pending"].append({
                                    "schedule_id": dag_id,
                                    "title": title,
                                    "description": description,
                                    "owner": owner,
                                    "status": "pending",
                                    "next_run_time": execution_time.isoformat()
                                })
                        except Exception as e:
                            logger.error(f"Error calculating next run for {dag_id}: {str(e)}")

                logger.info(
                    f"일별 통계 조회 결과 - 날짜: {target_date}, 성공: {len(result['success'])}, 실패: {len(result['failed'])}, 대기: {len(result['pending'])}")

        except Exception as e:
            logger.error(f"Error in get_dag_runs_by_date: {str(e)}")

        return result

    @staticmethod
    def get_all_schedules_with_details(
            user_id: int = None,
            page: int = 1,
            size: int = 20,
            title: str = "",
            owner: str = "",
            frequency: str = "",
            status: str = "active"
    ) -> Dict[str, Any]:
        """모든 스케줄(DAG) 목록을 반환 - DB 의존성 없는 버전"""
        try:
            # Airflow API에서 필요한 필드
            needed_fields = [
                "dag_id",
                "dag_display_name",
                "description",
                "is_paused",
                "owners",
                "schedule_interval",
                "next_dagrun_data_interval_end",
                "tags"  # 태그 추가
            ]

            # 페이지네이션 계산
            offset = (page - 1) * size

            # 상태 필터링 설정
            paused_param = None
            if status == "active":
                paused_param = False
            elif status == "paused":
                paused_param = True
            # status가 "all"인 경우 paused_param은 None 유지

            # Airflow API 호출 시 사용할 파라미터
            api_params = {
                "limit": 1000,  # 충분히 많은 수를 가져온 후 필터링
                "fields": needed_fields,
                "order_by": "-dag_id",  # ULID 역순 (최신순)
                "only_active": True
            }

            # 상태 필터링이 있는 경우에만 paused 매개변수 추가
            if paused_param is not None:
                api_params["paused"] = paused_param

            # Airflow API 호출
            dags_response = airflow_client.get_all_dags(**api_params)
            all_dags = dags_response.get("dags", [])

            # 메모리에서 필터링
            filtered_dags = all_dags

            # 제목 필터링
            if title:
                filtered_dags = [
                    dag for dag in filtered_dags
                    if (title.lower() in dag.get("dag_display_name", "").lower()) or
                       any(isinstance(tag, dict) and "name" in tag and
                           tag["name"].startswith("title:") and
                           title.lower() in tag["name"][6:].lower()
                           for tag in dag.get("tags", []))
                ]

            # 소유자 필터링
            if owner:
                filtered_dags = [
                    dag for dag in filtered_dags
                    if (owner.lower() in (dag.get("owners", [""])[0] or "").lower()) or
                       any(isinstance(tag, dict) and "name" in tag and
                           tag["name"].startswith("owner:") and
                           owner.lower() in tag["name"][6:].lower()
                           for tag in dag.get("tags", []))
                ]

            # 주기 필터링
            if frequency:
                filtered_dags = [
                    dag for dag in filtered_dags
                    if any(isinstance(tag, dict) and "name" in tag and
                           tag["name"].startswith("frequency:") and
                           frequency.lower() in tag["name"][10:].lower()
                           for tag in dag.get("tags", []))
                ]

            # 총 결과 수
            total_entries = len(filtered_dags)

            # 페이지네이션 적용
            start_idx = (page - 1) * size
            end_idx = min(start_idx + size, len(filtered_dags))
            paginated_dags = filtered_dags[start_idx:end_idx] if start_idx < len(filtered_dags) else []

            # 결과가 비어있으면 빈 결과 반환
            if not paginated_dags:
                return {
                    "schedules": [],
                    "total": total_entries
                }

            # 응답 데이터 구성
            schedule_list = []
            for dag in paginated_dags:
                dag_id = dag.get("dag_id")

                # 태그에서 메타데이터 추출
                parsed_tags = ScheduleService._parse_dag_tags(dag.get("tags", []))

                # 기본 정보 구성
                schedule_data = {
                    "schedule_id": dag_id,
                    "title": parsed_tags.get("title") or dag.get("dag_display_name", dag_id),
                    "description": parsed_tags.get("description") or dag.get("description", ""),
                    "is_paused": dag.get("is_paused", False),
                    "owner": parsed_tags.get("owner") or (
                        dag.get("owners", ["unknown"])[0] if dag.get("owners") else "unknown"
                    ),
                    "jobs": [],
                    "last_run": None,
                    "next_run": None
                }

                # 크론 및 주기 정보 설정
                cron_expr = parsed_tags.get("cron_expression")
                if not cron_expr:
                    # Airflow API에서 가져온 정보 사용
                    schedule_interval = dag.get("schedule_interval")
                    if isinstance(schedule_interval, dict) and "__type" in schedule_interval:
                        cron_expr = schedule_interval.get("__type", "")
                    else:
                        cron_expr = str(schedule_interval) if schedule_interval else ""

                frequency_str = parsed_tags.get("frequency") or cron_utils.convert_cron_to_frequency(cron_expr)
                execution_time = parsed_tags.get("execution_time") or cron_utils.extract_execution_time_from_cron(
                    cron_expr)

                schedule_data["frequency_display"] = {
                    "type": frequency_str,
                    "time": execution_time
                }

                # 날짜 정보 설정
                if "start_date" in parsed_tags:
                    schedule_data["start_date"] = parsed_tags["start_date"]

                # job 정보 설정
                jobs_json = parsed_tags.get("jobs")
                logger.info(f"DAG {dag_id} - Tags: {dag.get('tags', [])}")
                logger.info(f"DAG {dag_id} - Parsed tags: {parsed_tags}")
                if jobs_json:
                    logger.info(f"DAG {dag_id} - Jobs JSON from tags: {jobs_json}")
                    try:
                        jobs_data = json.loads(jobs_json)
                        logger.info(f"DAG {dag_id} - Parsed jobs data: {jobs_data}")
                        jobs = []
                        for idx, job_info in enumerate(sorted(jobs_data, key=lambda x: x["order"])):
                            logger.info(f"DAG {dag_id} - Processing job info: {job_info}")
                            jobs.append({
                                "id": job_info["job_id"],
                                "order": idx + 1  # 0-based to 1-based
                            })
                        schedule_data["jobs"] = jobs
                        logger.info(f"DAG {dag_id} - Final jobs list: {jobs}")

                    except:
                        logger.error(f"Error parsing jobs JSON from tags: {jobs_json}")

                # 최근 실행 정보 조회
                try:
                    recent_runs = airflow_client.get_dag_runs(dag_id, limit=1)
                    if recent_runs:
                        recent_run = recent_runs[0]
                        schedule_data["last_run"] = {
                            "run_id": recent_run.get("dag_run_id"),
                            "status": recent_run.get("state"),
                            "end_time": recent_run.get("end_date")
                        }
                except Exception as e:
                    logger.error(f"Error getting recent runs for {dag_id}: {str(e)}")

                # 다음 실행 예정 조회
                if dag.get("next_dagrun_data_interval_end"):
                    schedule_data["next_run"] = {
                        "scheduled_time": dag.get("next_dagrun_data_interval_end")
                    }
                else:
                    schedule_data["next_run"] = None

                schedule_list.append(schedule_data)

            return {
                "schedules": schedule_list,
                "total": total_entries
            }
        except Exception as e:
            logger.error(f"Error getting schedules from Airflow: {str(e)}")
            return {
                "schedules": [],
                "total": 0
            }