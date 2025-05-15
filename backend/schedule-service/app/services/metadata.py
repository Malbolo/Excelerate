import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings
from app.core.log_config import logger


def get_metadata_path(dag_id: str) -> str:
    """메타데이터 파일 경로 반환"""
    return os.path.join(settings.AIRFLOW_DAGS_PATH, f"{dag_id}.meta.json")

def get_dag_metadata(dag_id: str) -> Dict[str, Any]:
    """메타데이터 파일에서 DAG 추가 정보 조회"""
    default_metadata = {
        "job_ids": [],
        "start_date": None,
        "end_date": None,
        "success_emails": [],
        "failure_emails": [],
        "execution_time": None,
        "title": None,
        "description": None
    }

    meta_file_path = get_metadata_path(dag_id)

    # 새로운 JSON 형식
    if os.path.exists(meta_file_path):
        try:
            with open(meta_file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"메타데이터 파일 형식 오류: {str(e)}")
        except Exception as e:
            logger.error(f"메타데이터 파일 읽기 오류: {str(e)}")

    # 이전 형식 메타데이터가 있는지 확인 (마이그레이션 지원)
    old_meta_path = os.path.join(settings.AIRFLOW_DAGS_PATH, f"{dag_id}.meta")
    if os.path.exists(old_meta_path):
        try:
            metadata = default_metadata.copy()
            with open(old_meta_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("JOBS:"):
                        job_ids_str = line.split(':', 1)[1].strip()
                        metadata["job_ids"] = job_ids_str.split(',') if job_ids_str else []
                    elif line.startswith("START_DATE:"):
                        metadata["start_date"] = line.split(':', 1)[1].strip()
                    elif line.startswith("END_DATE:"):
                        end_date_str = line.split(':', 1)[1].strip()
                        if end_date_str.lower() != "none":
                            metadata["end_date"] = end_date_str
                    elif line.startswith("SUCCESS_EMAILS:"):
                        emails_str = line.split(':', 1)[1].strip()
                        metadata["success_emails"] = emails_str.split(',') if emails_str else []
                    elif line.startswith("FAILURE_EMAILS:"):
                        emails_str = line.split(':', 1)[1].strip()
                        metadata["failure_emails"] = emails_str.split(',') if emails_str else []
                    elif line.startswith("EXECUTION_TIME:"):
                        metadata["execution_time"] = line.split(':', 1)[1].strip()
                    elif line.startswith("TITLE:"):
                        metadata["title"] = line.split(':', 1)[1].strip()
                    elif line.startswith("DESCRIPTION:"):
                        metadata["description"] = line.split(':', 1)[1].strip()

            # 새 형식으로 저장
            save_dag_metadata(**metadata, dag_id=dag_id)

            # 이전 형식 파일 백업
            try:
                os.rename(old_meta_path, f"{old_meta_path}.bak")
                logger.info(f"이전 형식 메타데이터 파일 백업: {old_meta_path}.bak")
            except Exception as e:
                logger.warning(f"이전 형식 메타데이터 파일 백업 실패: {str(e)}")

            return metadata
        except Exception as e:
            logger.error(f"이전 형식 메타데이터 파일 읽기 오류: {str(e)}")

    return default_metadata

def save_dag_metadata(
        dag_id: str,
        job_ids: List[str],
        start_date: str,
        end_date: Optional[str] = None,
        success_emails: Optional[List[str]] = None,
        failure_emails: Optional[List[str]] = None,
        execution_time: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
) -> bool:
    """DAG 메타데이터 파일 저장"""

    metadata = {
        "dag_id": dag_id,
        "job_ids": job_ids,
        "start_date": start_date,
        "end_date": end_date,
        "success_emails": success_emails or [],
        "failure_emails": failure_emails or [],
        "execution_time": execution_time,
        "title": title,
        "description": description,
        "updated_at": datetime.now().isoformat()
    }

    meta_file_path = get_metadata_path(dag_id)

    try:
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(meta_file_path), exist_ok=True)

        # JSON 형식으로 저장
        with open(meta_file_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"메타데이터 파일 저장 완료: {meta_file_path}")
        return True
    except Exception as e:
        logger.error(f"메타데이터 파일 저장 오류: {str(e)}")
        return False