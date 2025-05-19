from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from croniter import croniter

from app.core.log_config import logger
from app.core.config import settings
from app.services.airflow_client import airflow_client
from app.utils import date_utils, cron_utils
from app.crud import schedule_crud
from app.db.database import SessionLocal
from app.utils.redis_calendar import RedisCalendarCache

calendar_cache = RedisCalendarCache(
    redis_url=settings.REDIS_URL,
    ttl_seconds=settings.REDIS_CALENDAR_CACHE_TTL
)

def build_monthly_dag_calendar(year: int, month: int, refresh: bool = False, db=None) -> Dict[str, Any]:
    """
    월별 DAG 실행 통계 생성 (캐싱 로직 포함)

    Args:
        year: 년도
        month: 월
        refresh: 캐시 무시 여부 (True면 캐시를 무시하고 새로 생성)
        db: 데이터베이스 세션 (None이면 새로 생성)

    Returns:
        Dictionary containing:
        - calendar_data: 달력 데이터
        - updated_at: 업데이트 시간 (ISO 형식)
        - cached: 캐시에서 가져왔는지 여부
    """
    # 캐시 확인 (refresh가 아닌 경우)
    if not refresh:
        cache_hit, cached_result = calendar_cache.get(year, month)
        if cache_hit:
            return {
                "calendar_data": cached_result["calendar_data"],
                "updated_at": cached_result["updated_at"],
                "cached": True
            }

    # 캐시 미스 또는 리프레시: 데이터 생성
    # Airflow에서 모든 DAG 목록 가져오기
    dags = airflow_client.get_all_dags()

    # 달력 데이터 생성
    calendar_data = _generate_calendar_data(dags, year, month, db)

    # 결과 캐싱
    calendar_cache.set(year, month, calendar_data)

    # 현재 시간 (방금 업데이트됨)
    now = datetime.now().isoformat()

    return {
        "calendar_data": calendar_data,
        "updated_at": now,
        "cached": False
    }

def _generate_calendar_data(dags: List[Dict[str, Any]], year: int, month: int, db=None) -> List[Dict[str, Any]]:
    """
    월별 DAG 실행 통계 생성 (현재까지는 실제 실행 이력, 미래는 예측 실행 기반)
    """
    close_db = False
    try:
        # DB 세션 생성 (제공되지 않은 경우)
        if db is None:
            db = SessionLocal()
            close_db = True

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
                "pending": 0,
                "running": 0
            })

        # Airflow 상태 그룹화 정의
        SUCCESS_STATES = ["success"]
        RUNNING_STATES = ["running", "queued", "scheduled", "up_for_reschedule", "restarting"]
        FAILED_STATES = ["failed", "upstream_failed", "shutdown", "removed", "up_for_retry"]

        # 날짜별 데이터 인덱스 구성 (빠른 조회용)
        date_index = {item["date"]: i for i, item in enumerate(all_days)}

        # DB에서 모든 스케줄 정보 가져오기
        db_schedules = {}
        try:
            all_db_schedules = schedule_crud.get_all_schedules(db)
            for schedule in all_db_schedules:
                db_schedules[schedule.id] = schedule
        except Exception as e:
            logger.error(f"Error getting DB data: {str(e)}")

        # DAG 별로 처리
        for dag in dags:
            dag_id = dag["dag_id"]

            # DB에서 스케줄 정보 가져오기
            db_schedule = db_schedules.get(dag_id)

            # 스케줄 표현식 추출 - DB에서 우선 가져오기
            cron_expr = None
            if db_schedule and hasattr(db_schedule, 'cron_expression'):
                cron_expr = db_schedule.cron_expression

            # DB에 없으면 Airflow에서 가져오기
            if not cron_expr:
                cron_expr = cron_utils.normalize_cron_expression(dag.get("schedule_interval"))

            if not cron_expr or not croniter.is_valid(cron_expr):
                logger.debug(f"Invalid or empty cron: {cron_expr} for DAG {dag_id}")
                continue

            # DAG의 시작일/종료일 추출
            dag_start_date, dag_end_date = _extract_dag_dates(dag, dag_id, now, db_schedule)

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
            dag_runs = airflow_client.get_dag_runs(
                dag_id,
                limit=100,
                start_date=start_date,
                end_date=end_date,
                fields=["start_date", "state", "dag_run_id"]
            )

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
                y, m, d = map(int, date_str.split("-"))
                date_dt = datetime(y, m, d, tzinfo=timezone.utc)
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
                            success_count = sum(1 for run in day_runs if run.get("state", "").lower() in SUCCESS_STATES)
                            running_count = sum(1 for run in day_runs if run.get("state", "").lower() in RUNNING_STATES)
                            failed_count = sum(1 for run in day_runs if run.get("state", "").lower() in FAILED_STATES)
                            pending_count = len(day_runs) - success_count - failed_count - running_count

                            all_days[idx]["success"] += success_count
                            all_days[idx]["running"] += running_count
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
                                # 이미 처리된 실행이 없는 경우에만 추가
                                if not day_runs:
                                    all_days[idx]["pending"] += 1
                        except Exception as e:
                            logger.debug(f"Error evaluating cron for {dag_id} on {date_str}: {str(e)}")
                    else:
                        # 과거 날짜는 실제 실행 이력만 고려
                        if day_runs:
                            success_count = sum(1 for run in day_runs if run.get("state", "").lower() in SUCCESS_STATES)
                            running_count = sum(1 for run in day_runs if run.get("state", "").lower() in RUNNING_STATES)
                            failed_count = sum(1 for run in day_runs if run.get("state", "").lower() in FAILED_STATES)

                            all_days[idx]["success"] += success_count
                            all_days[idx]["running"] += running_count
                            all_days[idx]["failed"] += failed_count

        # 모든 DAG 처리 후 각 날짜의 total 계산
        for idx, day_data in enumerate(all_days):
            all_days[idx]["total"] = day_data["success"] + day_data["failed"] + day_data["pending"] + day_data["running"]

        return all_days

    finally:
        # 생성한 경우에만 세션 닫기
        if close_db and db is not None:
            db.close()

def _extract_dag_dates(dag: Dict[str, Any], dag_id: str, now: datetime, db_schedule=None) -> Tuple[
    datetime, Optional[datetime]]:
    """DAG의 시작일과 종료일을 추출"""
    # DB에서 시작일 정보 가져오기 (우선)
    dag_start_date = None
    dag_end_date = None

    if db_schedule:
        # DB에 정보가 있으면 사용
        if hasattr(db_schedule, 'start_date') and db_schedule.start_date:
            # timezone 확인 및 추가
            dag_start_date = db_schedule.start_date
            if dag_start_date.tzinfo is None:
                dag_start_date = dag_start_date.replace(tzinfo=timezone.utc)

        if hasattr(db_schedule, 'end_date') and db_schedule.end_date:
            # timezone 확인 및 추가
            dag_end_date = db_schedule.end_date
            if dag_end_date.tzinfo is None:
                dag_end_date = dag_end_date.replace(tzinfo=timezone.utc)

    return dag_start_date, dag_end_date

def _is_dag_in_month_range(dag_id: str, dag_start_date: datetime, dag_end_date: Optional[datetime],
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