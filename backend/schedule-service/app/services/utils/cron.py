from typing import List, Dict, Any, Optional
from datetime import datetime
from croniter import croniter

def is_valid_cron(cron_expr: str) -> bool:
    """크론 표현식 유효성 검사"""
    return croniter.is_valid(cron_expr) if cron_expr else False

def generate_expected_run_dates(cron_expr: str, start_date: datetime, end_date: datetime) -> List[str]:
    """주어진 cron 표현식과 기간 내에서 실행 예정인 날짜 리스트 반환 (YYYY-MM-DD 형식)"""
    iter = croniter(cron_expr, start_date)
    result = []

    while True:
        next_run = iter.get_next(datetime)
        if next_run > end_date:
            break
        result.append(next_run.strftime("%Y-%m-%d"))

    return result

def extract_execution_time_from_cron(cron_expression: str) -> Optional[str]:
    """cron 표현식에서 실행 시간(HH:MM) 추출"""
    if not cron_expression:
        return None

    if isinstance(cron_expression, dict) and "__type" in cron_expression and cron_expression["__type"] == "CronExpression":
        cron_parts = cron_expression.get("value", "").split(" ")
    else:
        cron_parts = cron_expression.strip().split(" ")

    if len(cron_parts) >= 2:
        minute, hour = cron_parts[0], cron_parts[1]
        # 간단한 시간 형식인 경우만 처리 (*/2 같은 복잡한 패턴은 제외)
        if hour.isdigit() and minute.isdigit():
            return f"{int(hour):02d}:{int(minute):02d}"

    return None

def convert_cron_to_frequency(cron_expression: str) -> str:
    """cron 표현식을 사용자 친화적인 주기 표현으로 변환"""
    if not cron_expression:
        return ""

    parts = cron_expression.strip().split(" ")
    if len(parts) < 5:
        return cron_expression  # 유효하지 않은 cron 표현식은 그대로 반환

    minute, hour, day_of_month, month, day_of_week = parts[:5]

    # 일일 주기 (특정 시간에 매일)
    if day_of_month == "*" and month == "*" and day_of_week == "*":
        return "daily"

    # 주간 주기 (특정 요일마다)
    if day_of_month == "*" and month == "*" and day_of_week.isdigit():
        return "weekly"

    # 월간 주기 (매월 특정 일)
    if day_of_month.isdigit() and month == "*" and day_of_week == "*":
        return "monthly"

    # 시간 간격 주기
    if hour.startswith("*/") and day_of_month == "*" and month == "*" and day_of_week == "*":
        interval = hour.replace("*/", "")
        if interval.isdigit():
            return f"every_{interval}_hours"

    # 일 간격 주기
    if day_of_month.startswith("*/") and month == "*" and day_of_week == "*":
        interval = day_of_month.replace("*/", "")
        if interval.isdigit():
            # 7의 배수면 주 단위로 변환
            if int(interval) % 7 == 0 and int(interval) > 0:
                weeks = int(interval) // 7
                return f"every_{weeks}_weeks"
            return f"every_{interval}_days"

    # 변환할 수 없는 경우 원본 표현식 반환
    return cron_expression

def parse_cron_to_friendly_format(cron_expression: str) -> dict:
    """cron 표현식을 사용자 친화적인 형식으로 변환"""
    if not cron_expression:
        return None

    # cron 형식이 아닌 경우 처리
    if not isinstance(cron_expression, str) or cron_expression.count(" ") < 4:
        return None

    parts = cron_expression.strip().split()
    if len(parts) < 5:
        return None

    minute, hour, day_of_month, month, day_of_week = parts[:5]

    # 시간 형식 변환
    time_str = f"{int(hour):02d}:{int(minute):02d}" if hour.isdigit() and minute.isdigit() else "00:00"

    # 일간 (모든 날짜, 모든 월, 모든 요일)
    if day_of_month == "*" and month == "*" and day_of_week == "*":
        return {"type": "daily", "time": time_str}

    # 주간 (모든 날짜, 모든 월, 특정 요일)
    if day_of_month == "*" and month == "*" and day_of_week != "*":
        # 요일 변환 (0,7=일요일, 1=월요일, ..., 6=토요일)
        day_of_week_num = int(day_of_week) if day_of_week.isdigit() else 1
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        day_name = days[day_of_week_num % 7] if day_of_week_num != 7 else days[0]
        return {"type": "weekly", "dayOfWeek": day_name, "time": time_str}

    # 월간 (특정 날짜, 모든 월, 모든 요일)
    if day_of_month != "*" and month == "*" and (day_of_week == "*" or day_of_week == "?"):
        day = int(day_of_month) if day_of_month.isdigit() else 1
        return {"type": "monthly", "dayOfMonth": day, "time": time_str}

    # 기타 복잡한 경우 원본 cron 표현식 반환
    return {"type": "custom", "cronExpression": cron_expression}

def convert_frequency_to_cron(frequency: str, execution_time: str, start_date: Optional[datetime] = None) -> str:
    """
    사용자 친화적인 주기 표현을 cron 표현식으로 변환
    시작 날짜를 기준으로 weekly, monthly 주기 설정

    Args:
        frequency: 주기 표현 ("daily", "weekly", "monthly" 등)
        execution_time: "HH:MM" 형식의 실행 시간 (예: "09:30")
        start_date: 스케줄 시작 날짜 (선택적)
    """
    # 시간과 분 추출
    try:
        hour, minute = map(int, execution_time.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError("시간 형식이 잘못되었습니다. 형식은 'HH:MM'이어야 합니다.")
    except ValueError as e:
        raise ValueError(f"시간 형식이 잘못되었습니다. 형식은 'HH:MM'이어야 합니다. 상세: {str(e)}")

    # 이미 cron 표현식인 경우
    if frequency.count(" ") >= 4:
        return frequency

    if frequency == "daily":
        return f"{minute} {hour} * * *"
    elif frequency == "weekly":
        if start_date:
            day_of_week = start_date.weekday()
            cron_day = (day_of_week + 1) % 7
            return f"{minute} {hour} * * {cron_day}"
        else:
            # 기본값: 월요일 (1)
            return f"{minute} {hour} * * 1"
    elif frequency == "monthly":
        if start_date:
            # 시작 날짜의 일자에 실행
            day_of_month = start_date.day
            return f"{minute} {hour} {day_of_month} * *"
        else:
            # 기본값: 매월 1일
            return f"{minute} {hour} 1 * *"
    elif frequency.startswith("every_"):
        # every_2_days, every_3_hours 등의 형식 처리
        parts = frequency.split("_")
        if len(parts) == 3:
            interval = int(parts[1])
            unit = parts[2]

            if unit == "hours":
                if interval >= 24:
                    # hours는 24 미만이어야 함
                    raise ValueError("시간 간격은 24 미만이어야 합니다. 하루 이상은 days를 사용하세요.")
                return f"{minute} */{interval} * * *"
            elif unit == "days":
                return f"{minute} {hour} */{interval} * *"
            elif unit == "weeks":
                # 주 단위로는 cron에서 직접 지원하지 않으므로 7*interval 일로 변환
                return f"{minute} {hour} */{7 * interval} * *"

    # 알 수 없는 형식이면 기본값 (매일 정해진 시간)
    return f"{minute} {hour} * * *"