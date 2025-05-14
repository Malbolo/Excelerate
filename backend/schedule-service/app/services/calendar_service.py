from typing import List, Dict, Any
from datetime import datetime, timezone
import calendar
from croniter import croniter

from app.core.log_config import logger
from app.services.dag_query import get_dag_runs
from app.services.utils.cron import generate_expected_run_dates
from app.services.utils.time import get_month_date_range

def build_monthly_dag_calendar(dags: List[Dict[str, Any]], year: int, month: int) -> List[Dict[str, Any]]:
    """
    월별 DAG 실행 통계 생성 (현재까지는 실제 실행 이력, 미래는 예측 실행 기반)
    """
    # 타임존을 명시적으로 설정 (UTC 사용)
    first_day, last_day = get_month_date_range(year, month)

    # 현재 날짜와 시간
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

        # 스케줄 표현식 추출
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

        # 실행 이력 조회 (월 전체)
        dag_runs = get_dag_runs(dag_id, start_date=first_day.isoformat(), end_date=last_day.isoformat())

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
                        all_days[idx]["total"] += 1

                        success_count = sum(1 for run in day_runs if run.get("state", "").lower() == "success")
                        failed_count = sum(1 for run in day_runs if run.get("state", "").lower() in ["failed", "error"])

                        all_days[idx]["success"] += success_count
                        all_days[idx]["failed"] += failed_count

                        # 실행 중인 작업이 있는 경우
                        if len(day_runs) > success_count + failed_count:
                            all_days[idx]["pending"] += 1

                    # 현재 시간 이후 또는 미래 날짜의 크론 표현식 평가
                    try:
                        # 시작 시간 설정 (오늘의 경우 현재 시간, 미래의 경우 해당 날짜의 시작)
                        start_time = now if day_start <= now <= day_end else day_start

                        # 해당 날짜에 남은 시간에 실행되는 시간 찾기
                        cron_iter = croniter(cron_expr, start_time)
                        execution_time = cron_iter.get_next(datetime)

                        # 같은 날짜 내에 실행 시간이 있는지 확인
                        if execution_time <= day_end:
                            # 이미 처리된 실행이 없는 경우에만 추가
                            if not day_runs:
                                all_days[idx]["total"] += 1
                                all_days[idx]["pending"] += 1
                    except Exception as e:
                        logger.debug(f"Error evaluating cron for {dag_id} on {date_str}: {str(e)}")
                else:
                    # 과거 날짜는 실제 실행 이력만 고려
                    if day_runs:
                        all_days[idx]["total"] += 1

                        success_count = sum(1 for run in day_runs if run.get("state", "").lower() == "success")
                        failed_count = sum(1 for run in day_runs if run.get("state", "").lower() in ["failed", "error"])

                        all_days[idx]["success"] += success_count
                        all_days[idx]["failed"] += failed_count

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


def _process_dag_runs_for_calendar(dag_id, cron_expr, effective_start, effective_end,
                                   first_day, last_day, date_index, all_days):
    # 현재 시각 (UTC 기준)
    now = datetime.now(timezone.utc)

    # 실행 이력 조회
    dag_runs = get_dag_runs(dag_id, start_date=first_day.isoformat(), end_date=last_day.isoformat())
    executed_map = {run.get("start_date", "").split("T")[0]: run.get("state", "").lower() for run in dag_runs}

    # 해당 월의 각 날짜에 대해 크론 표현식 평가
    for date_str, idx in date_index.items():
        # 해당 날짜의 datetime 객체 생성
        date_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # 해당 날짜가 effective_start와 effective_end 사이에 있는지 확인
        if effective_start <= date_dt <= effective_end:
            # 해당 날짜의 0시 0분을 기준으로 크론 표현식 평가
            day_start = date_dt.replace(hour=0, minute=0, second=0)
            day_end = date_dt.replace(hour=23, minute=59, second=59)

            # 실행 결과가 있는지 확인
            state = executed_map.get(date_str)
            has_execution = state is not None

            try:
                # 해당 날짜에 실행되는 시간 찾기
                cron_iter = croniter(cron_expr, day_start)
                execution_time = cron_iter.get_next(datetime)

                # 같은 날짜 내에 실행 시간이 있는지 확인
                if execution_time <= day_end:
                    # 실행 결과가 있거나 미래 실행 시간이 있으면 total 증가
                    if has_execution or execution_time > now:
                        all_days[idx]["total"] += 1

                    # 실행 상태 확인
                    if state == "success":
                        all_days[idx]["success"] += 1
                    elif state in ("failed", "error"):
                        all_days[idx]["failed"] += 1
                    elif execution_time > now:
                        # 실행 이력이 없고, 예정 시간이 현재보다 미래인 경우만 pending으로 표시
                        all_days[idx]["pending"] += 1
            except Exception as e:
                logger.debug(f"Error evaluating cron for {dag_id} on {date_str}: {str(e)}")