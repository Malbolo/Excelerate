import re
from typing import Optional

def extract_error_message(logs: str) -> str:
    """로그에서 에러 메시지를 추출"""
    error_patterns = [
        r"([\w\.]+Error: .+)",
        r"([\w\.]+Exception: .+)",
        r"(ERROR: .+)",
        r"(Task failed with exception)"
    ]

    for pattern in error_patterns:
        matches = re.findall(pattern, logs)
        if matches:
            return matches[0]

    # 기본 에러 메시지
    return "작업 실행 중 오류가 발생했습니다."

def extract_error_trace(logs: str) -> str:
    """로그에서 스택 트레이스를 추출"""
    # 파이썬 스택 트레이스 패턴
    trace_pattern = r"Traceback \(most recent call last\):.*?(?=\n\n|\Z)"
    match = re.search(trace_pattern, logs, re.DOTALL)

    if match:
        return match.group(0)

    # 스택 트레이스가 없으면 로그 일부 반환 (너무 길지 않게)
    log_lines = logs.splitlines()
    if len(log_lines) > 20:
        return "\n".join(log_lines[-20:])  # 마지막 20줄만 반환

    return logs