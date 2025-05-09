from typing import List, Dict, Any
from datetime import datetime, timezone
import calendar
from croniter import croniter

from app.core.log_config import logger
from app.services.airflow.dag_query import get_dag_runs
from app.services.airflow.utils.cron import generate_expected_run_dates
from app.services.airflow.utils.time import get_month_date_range


def build_monthly_dag_calendar(dags: List[Dict[str, Any]], year: int, month: int) -> List[Dict[str, Any]]:
    """
    월별 DAG 실행 통계 생성 (pending 포함: 예상 실행일 기준)

    참고: 활성 상태인 DAG만 처리하며, DAG의 시작일 이후 날짜만 고려합니다.
    """
    # 타임존을 명시적으로 설정 (UTC 사용)
    first_day, last_day = get_month_date_range(year, month)

    # 현재 날짜
    now = datetime.now(timezone.utc)

    # 월의 모든 날짜를 미리 딕셔너리로 초기화
    all_days = []
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
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

        # 스케줄 표현식 추출 (객체인 경우와 문자열인 경우 모두 처리)
        raw_interval = dag.get("schedule_interval")
        cron_expr = ""

        if isinstance(raw_interval, dict):
            cron_expr = raw_interval.get("value", "")
        else:
            cron_expr = raw_interval or ""

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

        # 실행 예정일 계산 및 실행 이력 처리
        _process_dag_runs_for_calendar(dag_id, cron_expr, effective_start, effective_end,
                                       first_day, last_day, date_index, all_days)

    # 최종 결과 반환 (날짜별로 정렬된 상태로 유지)
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
        dag_start_date = _extract_date_from_dag_id(dag_id)

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


def _extract_date_from_dag_id(dag_id: str) -> datetime:
    """DAG ID에서 날짜 추출"""
    try:
        # DAG ID 형식: 'owner_name_YYYYMMDDHHMMSS'
        date_part = dag_id.split('_')[-1]

        # 날짜 부분이 숫자인지 확인
        if len(date_part) >= 8 and date_part.isdigit():
            year_part = int(date_part[:4])
            month_part = int(date_part[4:6])
            day_part = int(date_part[6:8])

            # 유효한 날짜인지 확인
            if 2000 <= year_part <= 2100 and 1 <= month_part <= 12 and 1 <= day_part <= 31:
                return datetime(year_part, month_part, day_part, tzinfo=timezone.utc)
    except (ValueError, IndexError) as e:
        logger.debug(f"Error extracting date from DAG ID {dag_id}: {str(e)}")
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


def _process_dag_runs_for_calendar(dag_id: str, cron_expr: str, effective_start: datetime,
                                   effective_end: datetime, first_day: datetime, last_day: datetime,
                                   date_index: Dict[str, int], all_days: List[Dict[str, Any]]):
    """DAG 실행 정보 처리하여 캘린더 데이터 구성"""
    try:
        logger.debug(f"Generating expected dates for {dag_id} from {effective_start} to {effective_end}")
        expected_dates = generate_expected_run_dates(cron_expr, effective_start, effective_end)
        logger.debug(f"Expected dates for {dag_id}: {expected_dates}")
    except Exception as e:
        logger.error(f"Error generating expected dates for {dag_id}: {e}")
        return

    # 실행 이력 조회
    try:
        dag_runs = get_dag_runs(
            dag_id,
            start_date=first_day.isoformat().replace("+00:00", "Z"),
            end_date=last_day.isoformat().replace("+00:00", "Z")
        )
        executed_map = {run.get("start_date", "").split("T")[0]: run.get("state", "").lower() for run in dag_runs}
    except Exception as e:
        logger.error(f"Error getting DAG runs for {dag_id}: {e}")
        executed_map = {}

    # 통계 누적 (날짜별 인덱스 사용)
    for date in expected_dates:
        if date in date_index:
            idx = date_index[date]
            all_days[idx]["total"] += 1

            state = executed_map.get(date)
            if state == "success":
                all_days[idx]["success"] += 1
            elif state in ("failed", "error"):
                all_days[idx]["failed"] += 1
            else:
                all_days[idx]["pending"] += 1