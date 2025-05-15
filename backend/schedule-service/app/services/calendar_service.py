from typing import List, Dict, Any
from datetime import datetime, timezone
from croniter import croniter

from app.core.log_config import logger
from app.services.airflow_client import airflow_client
from app.utils import date_utils, cron_utils

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
                            # 이미 처리된 실행이 없는 경우에만 추가
                            if not day_runs:
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