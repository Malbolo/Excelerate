from minio import Minio
from app.core.config import settings
import json
import io
import logging
from typing import Optional
from uuid import uuid4

logger = logging.getLogger("minio-client")


class MinioClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"버킷 '{self.bucket}' 생성됨.")
            else:
                logger.info(f"버킷 '{self.bucket}' 존재함.")
        except Exception as e:
            logger.error(f"버킷 확인 중 오류: {e}")
            raise

    # ─── JSON 전용 (기존) ─────────────────────────────────

    def save_data(self, object_name: str, data: dict) -> bool:
        """JSON 데이터를 MinIO에 저장"""
        j = json.dumps(data).encode("utf-8")
        stream = io.BytesIO(j)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=stream,
            length=len(j),
            content_type="application/json"
        )
        logger.info(f"JSON saved: {object_name}")
        return True

    def get_data(self, object_name: str) -> Optional[dict]:
        """MinIO에서 JSON 조회"""
        try:
            resp = self.client.get_object(self.bucket, object_name)
            data = json.loads(resp.read().decode("utf-8"))
            resp.close(); resp.release_conn()
            return data
        except Exception as e:
            logger.error(f"JSON get error ({object_name}): {e}")
            return None

    def exists(self, object_name: str) -> bool:
        """객체 존재 여부 확인"""
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except Exception:
            return False

    # ─── Excel 전용 메서드 ─────────────────────────────────

    def download_excel(self, object_name: str, local_path: str):
        """
        bucket 내 object_name(.xlsx)을 local_path 로 다운로드
        (binary)
        """
        try:
            self.client.fget_object(self.bucket, object_name, local_path)
            logger.info(f"Downloaded Excel: {object_name} -> {local_path}")
        except Exception as e:
            logger.error(f"Excel download failed ({object_name}): {e}")
            raise

    def upload_excel(self, object_name: str, local_path: str):
        """
        local_path 파일(.xlsx)을 bucket 의 object_name 으로 업로드
        """
        try:
            self.client.fput_object(
                bucket_name=self.bucket,
                object_name=object_name,
                file_path=local_path,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            logger.info(f"Uploaded Excel: {local_path} -> {object_name}")
        except Exception as e:
            logger.error(f"Excel upload failed ({local_path}): {e}")
            raise

    def presigned_download_url(self, object_name: str, expires: int = 3600) -> str:
        """
        해당 object 에 대한 presigned GET URL 생성 (초 단위 만료)
        """
        try:
            url = self.client.presigned_get_object(self.bucket, object_name, expires=expires)
            logger.info(f"Presigned URL created: {object_name}")
            return url
        except Exception as e:
            logger.error(f"Presigned URL error ({object_name}): {e}")
            raise

    # ─── 활용 예시 메서드 ─────────────────────────────────

    def download_template(self, template_name: str, local_path: str):
        """templates/{template_name}.xlsx 내려받기"""
        obj = f"templates/{template_name}.xlsx"
        self.download_excel(obj, local_path)

    def upload_result(self, user_id: str, template_name: str, local_path: str) -> str:
        """
        outputs/{user_id}/{template_name}_{uuid}.xlsx 로 업로드 후
        presigned URL 반환
        """
        obj = f"outputs/{user_id}/{template_name}_{uuid4().hex}.xlsx"
        self.upload_excel(obj, local_path)
        return self.presigned_download_url(obj)

minio_client = MinioClient()