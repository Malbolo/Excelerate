from pydantic.v1 import BaseSettings
from functools import lru_cache
from typing import List, Optional

class Settings(BaseSettings):
    # 애플리케이션 설정
    APP_NAME: str = "Schedule Service"
    APP_VERSION: str = "1.0.0"

    # Airflow 설정
    AIRFLOW__CORE__DAGS_FOLDER: str
    AIRFLOW_DAGS_PATH: str
    AIRFLOW_API_URL: str
    AIRFLOW_USERNAME: str
    AIRFLOW_PASSWORD: str

    # 서비스 URL
    JOB_SERVICE_URL: str
    USER_SERVICE_URL: Optional[str] = None

    # 개발 모드 설정
    DEV_MODE: bool = False

    # 로깅 설정
    LOG_LEVEL: str = "INFO"

    # Redis 설정
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # 캐시 설정
    REDIS_CALENDAR_CACHE_TTL: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **data):
        super().__init__(**data)

        # REDIS_URL이 직접 설정되지 않은 경우 다른 Redis 설정으로부터 구성
        if not self.REDIS_URL and self.REDIS_HOST:
            auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
            self.REDIS_URL = f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

@lru_cache()
def get_settings():
    """캐싱된 설정 인스턴스 반환"""
    return Settings()

settings = get_settings()