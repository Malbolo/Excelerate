from minio import Minio
from app.core.config import settings
import json
import io
import logging

logger = logging.getLogger("minio-client")

class MinioClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    # 버킷이 있는지 확인하고 없으면 생성
    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"버킷 '{self.bucket_name}'이 생성되었습니다.")
            else:
                logger.info(f"버킷 '{self.bucket_name}'이 이미 존재합니다.")
        except Exception as e:
            logger.error(f"버킷 확인/생성 중 오류 발생: {str(e)}")
            raise

    def save_data(self, object_name, data):
        """JSON 데이터를 MinIO에 저장"""
        try:
            json_data = json.dumps(data).encode('utf-8')
            data_stream = io.BytesIO(json_data)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(json_data),
                content_type='application/json'
            )
            logger.info(f"데이터가 '{object_name}'에 저장되었습니다.")
            return True
        except Exception as e:
            logger.error(f"데이터 저장 중 오류 발생: {str(e)}")
            raise

    def get_data(self, object_name):
        """MinIO에서 JSON 데이터 조회"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            data = json.loads(response.read().decode('utf-8'))
            response.close()
            response.release_conn()
            return data
        except Exception as e:
            logger.error(f"'{object_name}' 데이터 조회 중 오류 발생: {str(e)}")
            return None

    def check_if_exists(self, object_name):
        try:
            # 객체의 정보를 가져와 존재 여부 확인
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except Exception:
            # 객체가 없거나 오류 발생 시
            return False

minio_client = MinioClient()