import os
from typing import Dict, Any, List, Optional

def get_dag_metadata(dag_id: str) -> Dict[str, Any]:
    """메타데이터 파일에서 DAG 추가 정보 조회"""
    metadata = {
        "job_ids": [],
        "start_date": None,
        "end_date": None,
        "success_emails": [],
        "failure_emails": [],
        "execution_time": None,
        "title": None,  # title 필드 추가
        "description": None  # description 필드 추가 (선택사항)
    }

    meta_file_path = f"/opt/airflow/dags/{dag_id}.meta"
    if os.path.exists(meta_file_path):
        try:
            with open(meta_file_path, 'r') as f:
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
                    elif line.startswith("TITLE:"):  # TITLE 읽기 추가
                        metadata["title"] = line.split(':', 1)[1].strip()
                    elif line.startswith("DESCRIPTION:"):  # DESCRIPTION 읽기 추가
                        metadata["description"] = line.split(':', 1)[1].strip()
        except Exception as e:
            print(f"Error reading metadata file: {str(e)}")

    return metadata

def save_dag_metadata(
    dag_id: str,
    job_ids: List[str],
    start_date: str,
    end_date: Optional[str] = None,
    success_emails: Optional[List[str]] = None,
    failure_emails: Optional[List[str]] = None,
    execution_time: Optional[str] = None,
    title: Optional[str] = None,  # title 파라미터 추가
    description: Optional[str] = None  # description 파라미터 추가 (선택사항)
) -> bool:
    """DAG 메타데이터 파일 저장"""
    try:
        meta_file_path = f"/opt/airflow/dags/{dag_id}.meta"
        with open(meta_file_path, 'w') as f:
            f.write(f"JOBS:{','.join(job_ids)}\n")
            f.write(f"START_DATE:{start_date}\n")
            if end_date:
                f.write(f"END_DATE:{end_date}\n")
            else:
                f.write("END_DATE:None\n")
            f.write(f"SUCCESS_EMAILS:{','.join(success_emails or [])}\n")
            f.write(f"FAILURE_EMAILS:{','.join(failure_emails or [])}\n")
            f.write(f"EXECUTION_TIME:{execution_time or ''}\n")
            f.write(f"TITLE:{title or ''}\n")  # TITLE 저장 추가
            f.write(f"DESCRIPTION:{description or ''}\n")  # DESCRIPTION 저장 추가 (선택사항)
        return True
    except Exception as e:
        print(f"Error saving metadata file: {str(e)}")
        return False