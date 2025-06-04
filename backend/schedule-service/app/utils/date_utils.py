from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional


def get_month_date_range(year: int, month: int) -> Tuple[datetime, datetime]:
    """해당 월의 첫날과 마지막 날을 UTC timezone으로 반환"""
    # 해당 월의 첫 날 (1일)
    first_day = datetime(year, month, 1, tzinfo=timezone.utc)

    # 해당 월의 마지막 날 계산
    if month == 12:
        next_month_first_day = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        next_month_first_day = datetime(year, month + 1, 1, tzinfo=timezone.utc)

    # 마지막 날은 다음 달 첫 날에서 1일을 뺀 날짜
    last_day = next_month_first_day - timedelta(days=1)

    return first_day, last_day

def format_date_for_airflow(dt: datetime, as_zulu: bool = True) -> str:
    """Airflow API 호출에 적합한 날짜 형식으로 변환"""
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    iso_format = dt.isoformat()
    if as_zulu:
        return iso_format.replace("+00:00", "Z")
    return iso_format

def parse_date_string(date_str: str, default_timezone: bool = True) -> Optional[datetime]:
    """문자열을 datetime 객체로 변환, 다양한 형식 지원"""
    if not date_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 형식 (밀리초 포함, Z)
        "%Y-%m-%dT%H:%M:%SZ",  # ISO 형식 (Z)
        "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 형식 (밀리초, 타임존 오프셋)
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 형식 (타임존 오프셋)
        "%Y-%m-%dT%H:%M:%S.%f",  # ISO 형식 (밀리초)
        "%Y-%m-%dT%H:%M:%S",  # ISO 형식
        "%Y-%m-%d %H:%M:%S.%f",  # MySQL 형식 (밀리초)
        "%Y-%m-%d %H:%M:%S",  # MySQL 형식
        "%Y-%m-%d",  # 날짜만
    ]

    # Z를 +00:00로 변환
    if date_str.endswith("Z"):
        date_str = date_str[:-1] + "+00:00"

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # 타임존이 없는 경우 UTC 적용
            if default_timezone and dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {date_str}")

def calculate_duration_seconds(start_time: str, end_time: str) -> Optional[float]:
    """두 ISO 문자열 시간 간의 차이를 초 단위로 계산"""
    if not start_time or not end_time:
        return None

    try:
        start = parse_date_string(start_time)
        end = parse_date_string(end_time)
        if start and end:
            return (end - start).total_seconds()
        return None
    except ValueError as e:
        return None

def extract_date_from_dag_id(dag_id: str) -> Optional[datetime]:
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
    except (ValueError, IndexError):
        pass

    return None

def get_now_utc() -> datetime:
    """현재 시간을 UTC 기준으로 반환"""
    return datetime.now(timezone.utc)