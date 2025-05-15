from typing import Dict, Any, Type, Optional
from fastapi import HTTPException, status
from app.core.log_config import logger

class AppError(Exception):
    """애플리케이션 공통 예외 클래스"""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """리소스를 찾을 수 없는 경우의 예외"""

    def __init__(self, message: str = "요청한 리소스를 찾을 수 없습니다.", error_code: str = "NOT_FOUND"):
        super().__init__(message, status.HTTP_404_NOT_FOUND, error_code)

class ValidationError(AppError):
    """입력 유효성 검사 실패 예외"""

    def __init__(self, message: str = "입력 데이터가 유효하지 않습니다.", error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, error_code)

class AuthorizationError(AppError):
    """인증/권한 관련 예외"""

    def __init__(self, message: str = "권한이 없습니다.", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(message, status.HTTP_403_FORBIDDEN, error_code)

class ServiceError(AppError):
    """서비스 호출 실패 예외"""

    def __init__(self, message: str = "서비스 호출 중 오류가 발생했습니다.", error_code: str = "SERVICE_ERROR"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, error_code)

def handle_error(error: Exception) -> Dict[str, Any]:
    """예외를 표준화된 응답 형식으로 변환"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_message = str(error)
    error_code = "INTERNAL_SERVER_ERROR"

    if isinstance(error, AppError):
        status_code = error.status_code
        error_message = error.message
        error_code = error.error_code
    elif isinstance(error, HTTPException):
        status_code = error.status_code
        error_message = error.detail
        error_code = f"HTTP_{status_code}"

    # 로깅
    logger.error(f"Error: {error_code} - {error_message}")

    return {
        "result": "error",
        "error": {
            "code": error_code,
            "message": error_message
        }
    }, status_code

def create_success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """성공 응답 생성"""
    response = {"result": "success"}

    if data is not None:
        response["data"] = data

    if message:
        response["message"] = message

    return response