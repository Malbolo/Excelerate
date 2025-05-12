from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MINIO_ENDPOINT:     str
    MINIO_ACCESS_KEY:   str
    MINIO_SECRET_KEY:   str
    MINIO_USE_SSL:      bool = False
    MINIO_BUCKET_NAME:  str

settings = Settings()
