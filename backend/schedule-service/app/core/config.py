import os
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    AIRFLOW_API_URL: str = os.getenv("AIRFLOW_API_URL")
    AIRFLOW_USERNAME: str = os.getenv("AIRFLOW_USERNAME")
    AIRFLOW_PASSWORD: str = os.getenv("AIRFLOW_PASSWORD")

    class Config:
        env_file = ".env"

settings = Settings()