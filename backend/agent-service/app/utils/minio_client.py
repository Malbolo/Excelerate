from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import json
import io
import logging
from typing import Optional, List
from uuid import uuid4

logger = logging.getLogger("minio-client")

class MinioClient:
    def __init__(self):
        # MinIO 클라이언트 초기화
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        # 기본 버킷 설정
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

    # ─── JSON 전용 메서드 ─────────────────────────────────

    def save_data(self, object_name: str, data: dict) -> bool:
        """JSON 데이터를 MinIO에 저장"""
        payload = json.dumps(data).encode("utf-8")
        stream = io.BytesIO(payload)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=stream,
            length=len(payload),
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

    def download_excel(self, object_name: str, local_path: str) -> None:
        """
        bucket 내 object_name(.xlsx)을 local_path 로 다운로드
        """
        try:
            self.client.fget_object(self.bucket, object_name, local_path)
            logger.info(f"Downloaded Excel: {object_name} -> {local_path}")
        except Exception as e:
            logger.error(f"Excel download failed ({object_name}): {e}")
            raise

    def upload_excel(self, object_name: str, local_path: str) -> None:
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

    # ─── 템플릿 CRUD ─────────────────────────────────

    def upload_template(self, template_name: str, local_file_path: str) -> None:
        """
        templates/{template_name}.xlsx 로 업로드 (없으면 생성, 있으면 덮어쓰기)
        """
        object_name = f"templates/{template_name}.xlsx"
        self.upload_excel(object_name, local_file_path)
        logger.info(f"Template uploaded: {template_name}")

    def list_templates(self) -> List[str]:
        """
        templates 버킷 내 모든 .xlsx 템플릿 이름(확장자 제외)을 반환
        """
        names: List[str] = []
        for obj in self.client.list_objects(self.bucket, prefix="templates/", recursive=True):
            name = obj.object_name
            if name.lower().endswith(".xlsx"):
                # "templates/" 이후 이름에서 ".xlsx" 제거
                tpl = name.split("/", 1)[1][:-5]
                names.append(tpl)
        return names

    def download_template(self, template_name: str, local_path: str) -> None:
        """
        templates/{template_name}.xlsx 을 local_path 로 다운로드
        """
        object_name = f"templates/{template_name}.xlsx"
        self.download_excel(object_name, local_path)

    def delete_template(self, template_name: str) -> None:
        """
        templates/{template_name}.xlsx 객체를 삭제
        """
        object_name = f"templates/{template_name}.xlsx"
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"Template deleted: {template_name}")
        except Exception as e:
            logger.error(f"Template delete failed ({template_name}): {e}")
            raise

    # ─── 결과 업로드 예시 ─────────────────────────────────

    def upload_result(self, user_id: str, template_name: str, local_path: str) -> str:
        """
        outputs/{user_id}/{template_name}_{uuid}.xlsx 로 업로드 후
        presigned URL 반환
        """
        object_name = f"outputs/{user_id}/{template_name}_{uuid4().hex}.xlsx"
        self.upload_excel(object_name, local_path)
        return self.presigned_download_url(object_name)

# 모듈 단일 인스턴스 제공
minio_client = MinioClient()