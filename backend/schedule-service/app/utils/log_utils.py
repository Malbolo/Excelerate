import re
import logging

# 정규식 패턴 미리 컴파일
ERROR_PATTERNS = [
    re.compile(r"([\w\.]+Error: .+)"),
    re.compile(r"([\w\.]+Exception: .+)"),
    re.compile(r"(ERROR: .+)"),
    re.compile(r"(Task failed with exception)")
]

TRACE_PATTERN = re.compile(r"Traceback \(most recent call last\):.*?(?=\n\n|\Z)", re.DOTALL)

def extract_error_message(logs: str) -> str:
    """로그에서 에러 메시지를 추출"""
    if not logs:
        return "로그가 비어 있습니다."

    # 혹시 바이트 타입이면 UTF-8로 디코딩
    if isinstance(logs, bytes):
        logs = logs.decode('utf-8')

    # 인코딩 이슈가 있을 수 있는 문자열을 처리
    # 이미 utf-8로 인코딩된 문자열이 다시 디코딩되는 경우 방지
    try:
        if not isinstance(logs, str):
            logs = str(logs)
    except Exception as e:
        return f"로그 처리 중 오류 발생: {str(e)}"

    for pattern in ERROR_PATTERNS:
        matches = pattern.findall(logs)
        if matches:
            return matches[0]

    # 기본 에러 메시지
    return "작업 실행 중 오류가 발생했습니다."

def extract_error_trace(logs: str) -> str:
    """로그에서 스택 트레이스를 추출"""
    if not logs:
        return ""

    # 혹시 바이트 타입이면 UTF-8로 디코딩
    if isinstance(logs, bytes):
        logs = logs.decode('utf-8')

    # 인코딩 이슈가 있을 수 있는 문자열을 처리
    try:
        if not isinstance(logs, str):
            logs = str(logs)
    except Exception as e:
        return f"로그 처리 중 오류 발생: {str(e)}"

    # 파이썬 스택 트레이스 패턴
    match = TRACE_PATTERN.search(logs)

    if match:
        return match.group(0)

    # 스택 트레이스가 없으면 로그 일부 반환 (너무 길지 않게)
    log_lines = logs.splitlines()
    if len(log_lines) > 20:
        return "\n".join(log_lines[-20:])  # 마지막 20줄만 반환

    return logs

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """로거 설정 유틸리티"""
    logger = logging.getLogger(name)

    # 로그 레벨 설정
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # 핸들러가 없는 경우에만 추가
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger