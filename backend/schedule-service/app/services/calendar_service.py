from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from croniter import croniter

from app.core.log_config import logger
from app.core.config import settings
from app.services.airflow_client import airflow_client
from app.utils import date_utils, cron_utils
# DB 관련 import 제거
# from app.crud import schedule_crud
# from app.db.database import SessionLocal
from app.utils.redis_calendar import RedisCalendarCache

calendar_cache = RedisCalendarCache(
    redis_url=settings.REDIS_URL,
    ttl_seconds=settings.REDIS_CALENDAR_CACHE_TTL
)


def build_monthly_dag_calendar(year: int, month: int) -> Dict[str, Any]:
    """
    월별 DAG 실행 통계 생성 (캐싱 로직 포함)

    Args:
        year: 년도
        month: 월

    Returns:
        Dictionary containing:
        - calendar_data: 달력 데이터
        - updated_at: 업데이트 시간 (ISO 형식)
        - cached: 캐시에서 가져왔는지 여부
    """
    cache_hit, cached_result = calendar_cache.get(year, month)
    if cache_hit:
        calendar_data = cached_result.get("calendar_data", [])

        return {
            "data": {
                "monthly": calendar_data,
                "updated_at": cached_result.get("updated_at"),
                "cached": True
            }
        }

    # 캐시 미스 또는 리프레시: 데이터 생성
    # Airflow에서 모든 DAG 목록 가져오기
    dags = airflow_client.get_all_dags().get("dags", [])
    logger.info(f"Retrieved {len(dags)} DAGs from Airflow")

    # 달력 데이터 생성
    calendar_data = _generate_calendar_data(dags, year, month)

    # 결과 캐싱
    calendar_cache.set(year, month, calendar_data)

    # 현재 시간 (방금 업데이트됨)
    now = date_utils.get_now_utc().isoformat()

    return {
        "data": {
            "monthly": calendar_data,
            "updated_at": now,
            "cached": False
        }
    }


def clear_monthly_cache(year: int, month: int):
    """
    특정 년월의 DAG 실행 통계 캐시를 삭제합니다.

    Args:
        year: 년도
        month: 월

    Returns:
        bool: 삭제 성공 여부
    """
    try:
        # Redis 캐시에서 해당 년월의 캐시 삭제
        calendar_cache.invalidate(year, month)
        return True

    except Exception as e:
        logger.error(f"캐시 삭제 중 오류 발생: {str(e)}")
        raise Exception(f"캐시 삭제에 실패했습니다: {str(e)}")


def _generate_calendar_data(dags: List[Dict[str, Any]], year: int, month: int) -> List[Dict[str, Any]]:
    """
    월별 DAG 실행 통계 생성 (현재까지는 실제 실행 이력, 미래는 예측 실행 기반)
    """
    try:
        # 타임존을 명시적으로 설정 (UTC 사용)
        first_day, last_day = date_utils.get_month_date_range(year, month)
        logger.info(f"Date range: {first_day} to {last_day}")

        # 현재 날짜와 시간
        now = date_utils.get_now_utc()
        logger.info(f"Current UTC time: {now}")

        # 오늘 날짜 로깅 (UTC 기준)
        today_str = now.strftime("%Y-%m-%d")
        logger.info(f"Today (UTC): {today_str}")

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

        logger.info(f"State groups defined: SUCCESS={SUCCESS_STATES}, RUNNING={RUNNING_STATES}, FAILED={FAILED_STATES}")

        # 날짜별 데이터 인덱스 구성 (빠른 조회용)
        date_index = {item["date"]: i for i, item in enumerate(all_days)}

        # DAG 별로 처리
        for dag in dags:
            dag_id = dag["dag_id"]

            # 태그에서 메타데이터 추출
            parsed_tags = _parse_dag_tags(dag)

            # 스케줄 표현식 추출 - 태그에서 가져오기
            cron_expr = parsed_tags.get("cron_expression")

            # 태그에 없으면 Airflow에서 가져오기
            if not cron_expr:
                cron_expr = cron_utils.normalize_cron_expression(dag.get("schedule_interval"))

            if not cron_expr or not croniter.is_valid(cron_expr):
                logger.debug(f"Invalid or empty cron: {cron_expr} for DAG {dag_id}")
                continue

            # DAG의 시작일/종료일 추출 (태그 기반)
            dag_start_date, dag_end_date = _extract_dag_dates_from_tags(parsed_tags, dag_id, now)

            # 범위 체크: 이 달의 날짜와 겹치는지 확인
            if not _is_dag_in_month_range(dag_id, dag_start_date, dag_end_date, first_day, last_day):
                continue

            # 유효한 시작일과 종료일 설정
            if dag_start_date:
                # 시작일의 경우 해당 날짜의 시작(00:00:00)으로 설정
                dag_start_day = dag_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                effective_start = max(dag_start_day, first_day)
            else:
                effective_start = first_day

            if dag_end_date:
                # 종료일의 경우 해당 날짜의 끝(23:59:59)으로 설정
                dag_end_day = dag_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                effective_end = min(dag_end_day, last_day)
            else:
                effective_end = last_day

            logger.info(f"DAG {dag_id} effective date range: {effective_start} to {effective_end}")

            if effective_start > effective_end:
                logger.debug(f"{dag_id} effective_start {effective_start} > effective_end {effective_end}")
                continue

            # 실행 이력 조회 (월 전체)
            start_date = date_utils.format_date_for_airflow(first_day)
            end_date = date_utils.format_date_for_airflow(last_day)
            logger.info(f"Querying runs for {dag_id} from {start_date} to {end_date}")

            dag_runs = airflow_client.get_dag_runs(
                dag_id,
                limit=100,
                start_date=start_date,
                end_date=end_date,
                fields=["start_date", "state", "dag_run_id"]
            )
            logger.info(f"Retrieved {len(dag_runs)} runs for DAG {dag_id}")

            # 날짜별 실행 이력 구성
            executed_runs_by_date = {}
            for run in dag_runs:
                original_date = run.get("start_date", "")
                run_date_str = run.get("start_date", "").split("T")[0]
                state = run.get("state", "").lower()

                if run_date_str == "2025-05-19":
                    logger.info(
                        f"TODAY RUN: DAG={dag_id}, ID={run.get('dag_run_id')}, State={state}, Time={original_date}")

                if run_date_str:
                    if run_date_str not in executed_runs_by_date:
                        executed_runs_by_date[run_date_str] = []
                    executed_runs_by_date[run_date_str].append(run)
            logger.info(f"Processed runs by date: {list(executed_runs_by_date.keys())}")

            # 해당 월의 각 날짜에 대해 데이터 처리
            for date_str, idx in date_index.items():
                # 해당 날짜의 datetime 객체 생성
                y, m, d = map(int, date_str.split("-"))
                date_dt = datetime(y, m, d, tzinfo=timezone.utc)
                day_start = date_dt.replace(hour=0, minute=0, second=0)
                day_end = date_dt.replace(hour=23, minute=59, second=59)

                # 날짜 비교를 위해 시간을 제거한 날짜 객체 사용
                date_dt_day = date_dt.replace(hour=0, minute=0, second=0, microsecond=0)

                # 특별히 오늘 날짜 조건 로깅
                if date_str == "2025-05-19":
                    is_today = (day_start <= now <= day_end)
                    in_effective_range = (effective_start <= date_dt <= effective_end)
                    logger.info(
                        f"Processing TODAY {dag_id}: is_today={is_today}, in_effective_range={in_effective_range}")
                    logger.info(f"  now={now}, day_start={day_start}, day_end={day_end}")
                    logger.info(
                        f"  effective_start={effective_start}, date_dt={date_dt}, effective_end={effective_end}")

                # 해당 날짜가 effective_start와 effective_end 사이에 있는지 확인
                if effective_start <= date_dt_day <= effective_end:
                    # 실행 이력 확인
                    day_runs = executed_runs_by_date.get(date_str, [])

                    if date_str == "2025-05-19":
                        logger.info(f"TODAY: Found {len(day_runs)} runs for DAG {dag_id}")

                    # 날짜가 오늘이고 아직 실행 시간이 오지 않았거나, 미래 날짜인 경우 크론 표현식 평가
                    if day_end > now:
                        if date_str == "2025-05-19":
                            logger.info(f"TODAY: day_end > now condition met")

                        # 오늘의 경우, 현재 시간까지의 실행 이력 처리
                        if day_start <= now <= day_end and day_runs:
                            logger.info(f"Processing TODAY's runs for DAG {dag_id}: found {len(day_runs)} runs")
                            # 각 실행의 상태 로깅
                            for i, run in enumerate(day_runs):
                                state = run.get("state", "").lower()
                                logger.info(f"  Run {i + 1}: ID={run.get('dag_run_id')}, State={state}")
                                if state in SUCCESS_STATES:
                                    logger.info(f"    Counted as SUCCESS")
                                elif state in RUNNING_STATES:
                                    logger.info(f"    Counted as RUNNING")
                                elif state in FAILED_STATES:
                                    logger.info(f"    Counted as FAILED")
                                else:
                                    logger.info(f"    Counted as PENDING (unknown state)")
                            # 오늘 이미 실행된 것이 있다면 처리
                            success_count = sum(1 for run in day_runs if run.get("state", "").lower() in SUCCESS_STATES)
                            running_count = sum(1 for run in day_runs if run.get("state", "").lower() in RUNNING_STATES)
                            failed_count = sum(1 for run in day_runs if run.get("state", "").lower() in FAILED_STATES)
                            pending_count = len(day_runs) - success_count - failed_count - running_count

                            if date_str == "2025-05-19":
                                logger.info(
                                    f"TODAY DAG {dag_id}: success={success_count}, running={running_count}, failed={failed_count}, pending={pending_count}")
                            logger.info(
                                f"  Final counts: success={success_count}, running={running_count}, failed={failed_count}, pending={pending_count}")

                            all_days[idx]["success"] += success_count
                            all_days[idx]["running"] += running_count
                            all_days[idx]["failed"] += failed_count
                            if pending_count > 0:
                                all_days[idx]["pending"] += pending_count
                            if date_str == "2025-05-19":
                                curr_values = all_days[idx].copy()
                                logger.info(f"TODAY after adding {dag_id}: {curr_values}")
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
            date_str = day_data["date"]
            all_days[idx]["total"] = day_data["success"] + day_data["failed"] + day_data["pending"] + day_data[
                "running"]

            if date_str == "2025-05-19":
                logger.info(f"TODAY'S FINAL DATA: {day_data}")
        logger.info(f"All dates with runs: {list(executed_runs_by_date.keys())}")
        return all_days

    except Exception as e:
        logger.error(f"Error generating calendar data: {str(e)}")
        raise


def _parse_dag_tags(dag: Dict[str, Any]) -> Dict[str, str]:
    """DAG 태그에서 메타데이터 추출 - 객체 형식 태그 처리"""
    parsed_tags = {}
    tags = dag.get("tags", [])

    # 객체 형식 태그 처리
    for tag in tags:
        # 객체 형식의 태그 처리 ({"name": "key:value"})
        if isinstance(tag, dict) and "name" in tag:
            tag_value = tag["name"]
            if isinstance(tag_value, str) and ":" in tag_value:
                key, value = tag_value.split(":", 1)
                parsed_tags[key] = value

    return parsed_tags

def _extract_dag_dates_from_tags(parsed_tags: Dict[str, str], dag_id: str, now: datetime) -> Tuple[
    Optional[datetime], Optional[datetime]]:
    """태그에서 DAG의 시작일과 종료일을 추출"""
    dag_start_date = None
    dag_end_date = None

    # 태그에서 시작일/종료일 추출
    start_date_str = parsed_tags.get('start_date')
    end_date_str = parsed_tags.get('end_date')

    # 시작일 파싱
    if start_date_str:
        try:
            # YYYY-MM-DD 형식 파싱
            if '-' in start_date_str:
                year, month, day = map(int, start_date_str.split('-'))
                dag_start_date = datetime(year, month, day, tzinfo=timezone.utc)
            else:
                logger.debug(f"Could not parse start_date format for DAG {dag_id}: {start_date_str}")
        except Exception as e:
            logger.debug(f"Error parsing start_date for DAG {dag_id}: {str(e)}")

    # 종료일 파싱
    if end_date_str and end_date_str.lower() != 'none':
        try:
            # YYYY-MM-DD 형식 파싱
            if '-' in end_date_str:
                year, month, day = map(int, end_date_str.split('-'))
                dag_end_date = datetime(year, month, day, tzinfo=timezone.utc)
            else:
                logger.debug(f"Could not parse end_date format for DAG {dag_id}: {end_date_str}")
        except Exception as e:
            logger.debug(f"Error parsing end_date for DAG {dag_id}: {str(e)}")

    return dag_start_date, dag_end_date


def _is_dag_in_month_range(dag_id: str, dag_start_date: Optional[datetime], dag_end_date: Optional[datetime],
                           first_day: datetime, last_day: datetime) -> bool:
    """DAG가 해당 월의 범위 내에 있는지 확인"""
    # 1. DAG 시작일이 이 달의 마지막 날보다 나중이면 스킵
    if dag_start_date and dag_start_date > last_day:
        logger.debug(f"{dag_id} start_date {dag_start_date} is after this month's last day {last_day}")
        return False

    # 2. DAG 종료일이 있고, 이 달의 첫째 날보다 이전이면 스킵
    if dag_end_date and dag_end_date < first_day:
        logger.debug(f"{dag_id} end_date {dag_end_date} is before this month's first day {first_day}")
        return False

    return True