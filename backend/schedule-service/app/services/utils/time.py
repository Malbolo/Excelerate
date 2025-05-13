from datetime import datetime, timezone
import calendar


def get_month_date_range(year: int, month: int):
    """월의 시작일과 종료일 반환"""
    first_day = datetime(year, month, 1, tzinfo=timezone.utc)
    _, last_day_num = calendar.monthrange(year, month)
    last_day = datetime(year, month, last_day_num, 23, 59, 59, tzinfo=timezone.utc)
    return first_day, last_day


def format_date_for_airflow(dt: datetime, as_zulu: bool = True) -> str:
    """Airflow API 호출에 적합한 날짜 형식으로 변환"""
    iso_format = dt.isoformat()
    if as_zulu:
        return iso_format.replace("+00:00", "Z")
    return iso_format


def calculate_duration_seconds(start_time: str, end_time: str) -> float:
    """두 ISO 문자열 시간 간의 차이를 초 단위로 계산"""
    if not start_time or not end_time:
        return None

    start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    return (end - start).total_seconds()