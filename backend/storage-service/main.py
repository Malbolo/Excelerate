from fastapi import FastAPI
from app.api.factory_routes import router
import logging
from app.api.init_dummy_data import create_comprehensive_factory_data
from app.core.minio_client import minio_client

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
app.include_router(router, prefix="/mes", tags=["MES 공장 데이터"])

@app.on_event("startup")
async def startup_event():
    # MinIO에 기본 데이터가 있는지 확인
    try:
        # 가장 기본적인 데이터 파일 중 하나를 확인
        check_file = "factory/basic_info.json"

        # 파일 존재 여부 확인
        file_exists = minio_client.check_if_exists(check_file)

        if not file_exists:
            logging.debug("MinIO에 기본 데이터가 없습니다. 더미 데이터를 생성합니다.")
            create_comprehensive_factory_data()
        else:
            logging.debug("MinIO에 이미 데이터가 존재합니다. 더미 데이터 생성을 건너뜁니다.")
    except Exception as e:
        logging.debug(f"데이터 확인 중 오류 발생: {str(e)}")
        logging.debug("오류가 발생하여 더미 데이터 생성을 진행합니다.")
        create_comprehensive_factory_data()

@app.get("/", tags=["기본"])
async def root():
    return {
        "message": "공장 MES API 서버",
        "version": "1.0.0",
        "endpoints": {
            "공장 데이터": "/mes/factory-data/..."
        }
    }

@app.get("/health", tags=["기본"])
async def health_check():
    return {"status": "healthy"}
