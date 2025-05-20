# app/core/config.py
import os
from typing import List, Optional
from pydantic_settings import BaseSettings

# 먼저 ENV 환경변수를 읽어와서 개발 환경 여부를 판단합니다.
if os.getenv("ENV", "DEV") == "DEV":
    from dotenv import load_dotenv
    load_dotenv(override=True) # 개발환경이라면 환경변수를 직접 주입하여 사용합니다.


class Settings(BaseSettings):
    APP_NAME: str = "Excelerate Agent Server"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str]

    # 개발환경 설정
    ENV: str

    # LangSmith 설정
    LANGSMITH_TRACING: bool
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str

    # OpenAI 설정
    OPENAI_API_KEY: str

    # Milvus 설정
    MILVUS_HOST: str
    MILVUS_PORT: str
    MILVUS_COLLECTION: str

    # Minio 설정
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_USE_SSL: bool
    MINIO_BUCKET_NAME: str

    # Filesystem URL 설정
    FILESYSTEM_URL: str

    TOKEN_SECRET_KEY: str

    # Redis 설정
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str

    # .env 파일을 읽어들여 주입. 배포 시 Jenkins Credential을 활용해 .env를 생성해 주입할 것
    class Config:
        env_file = ".env"


settings = Settings()
