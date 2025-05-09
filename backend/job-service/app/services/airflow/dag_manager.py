import os
import shutil
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.core.log_config import logger
from app.db.database import get_db
from app.models.models import Job
from app.services.airflow.dag_query import get_dag_detail
from app.services.airflow.execution import toggle_dag_pause
from app.services.airflow.metadata import save_dag_metadata, get_dag_metadata

def create_dag(
        name: str,
        description: str,
        cron_expression: str,
        job_ids: List[str],
        owner: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        success_emails: List[str] = None,
        failure_emails: List[str] = None,
        execution_time: str = None
) -> str:
    """새로운 DAG를 생성합니다."""
    # DAG ID는 고유해야 함
    dag_id = f"{owner}_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # MySQL에서 job 정보 가져오기
    db = next(get_db())
    try:
        job_details = []

        for job_id in job_ids:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise Exception(f"Job ID {job_id}를 찾을 수 없습니다.")
            job_details.append({
                "id": job.id,
                "name": job.title,
                "code": job.code
            })

        # 시작일과 종료일 문자열로 변환
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "None"

        # 태그 및 설명 설정
        tags_str = f"['custom', '{owner}', 'start_date:{start_date_str}', 'title:{name}'"
        if end_date:
            tags_str += f", 'end_date:{end_date_str}'"
        tags_str += "]"

        enhanced_description = f"{description} (Start: {start_date_str})"
        if end_date:
            enhanced_description += f", End: {end_date_str}"

        # DAG 코드 생성
        dag_code = _generate_dag_code(
            dag_id, owner, start_date, end_date, success_emails, failure_emails,
            enhanced_description, cron_expression, tags_str, job_details
        )

        # DAG 파일 저장
        _save_dag_file(dag_id, dag_code)

        # 메타데이터 파일 생성
        save_dag_metadata(
            dag_id=dag_id,
            job_ids=job_ids,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat() if end_date else None,
            success_emails=success_emails,
            failure_emails=failure_emails,
            execution_time=execution_time,
            title=name,
            description=description  # 설명 정보 전달
        )

        return dag_id

    finally:
        db.close()


def update_dag(
        dag_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        cron_expression: Optional[str] = None,
        job_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success_emails: Optional[List[str]] = None,
        failure_emails: Optional[List[str]] = None
) -> bool:
    """기존 DAG 업데이트 - 동일한 DAG ID를 유지하면서 내용만 교체"""
    try:
        # 기존 DAG 정보 조회
        current_dag = get_dag_detail(dag_id)
        dag_file_path = f"/opt/airflow/dags/{dag_id}.py"
        meta_file_path = f"/opt/airflow/dags/{dag_id}.meta"

        # DAG ID에서 owner 추출
        parts = dag_id.split('_')
        owner = parts[0]  # 기본값

        # 태그에서 owner 확인
        tags = current_dag.get("tags", [])
        for tag in tags:
            tag_value = tag
            if isinstance(tag, dict) and "name" in tag:
                tag_value = tag["name"]
            if tag_value.startswith("user_"):
                owner = tag_value
                break

        # 업데이트할 값 설정
        current_name = current_dag.get("name", "")
        current_description = current_dag.get("description", "")
        current_schedule = current_dag.get("schedule_interval", "")

        update_name = name if name is not None else current_name
        update_description = description if description is not None else current_description
        update_schedule = cron_expression if cron_expression is not None else current_schedule

        # 시작일과 종료일 설정
        start_date_dt = None
        end_date_dt = None

        # 태그에서 시작일과 종료일 추출
        for tag in tags:
            tag_value = tag
            if isinstance(tag, dict) and "name" in tag:
                tag_value = tag["name"]

            if tag_value.startswith("start_date:"):
                start_date_str = tag_value.split(':', 1)[1]
                try:
                    start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                except ValueError:
                    pass

            if tag_value.startswith("end_date:"):
                end_date_str = tag_value.split(':', 1)[1]
                if end_date_str != "None":
                    try:
                        end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
                    except ValueError:
                        pass

        # 변경할 시작일/종료일
        update_start_date = start_date if start_date is not None else start_date_dt
        update_end_date = end_date if end_date is not None else end_date_dt

        if update_start_date is None:
            raise Exception("시작일을 찾을 수 없습니다.")

        # job 정보 가져오기
        job_details = []
        if job_ids:
            db = next(get_db())
            try:
                for job_id in job_ids:
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if not job:
                        raise Exception(f"Job ID {job_id}를 찾을 수 없습니다.")
                    job_details.append({
                        "id": job.id,
                        "name": job.title,
                        "code": job.code
                    })
            finally:
                db.close()
        else:
            # 기존 메타 파일에서 job 목록 가져오기
            try:
                metadata = get_dag_metadata(dag_id)
                existing_job_ids = metadata.get("job_ids", [])

                if existing_job_ids:
                    db = next(get_db())
                    try:
                        for job_id in existing_job_ids:
                            job = db.query(Job).filter(Job.id == job_id).first()
                            if job:
                                job_details.append({
                                    "id": job.id,
                                    "name": job.title,
                                    "code": job.code
                                })
                    finally:
                        db.close()
            except Exception as e:
                logger.error(f"기존 job 정보 조회 실패: {str(e)}")
                raise Exception(f"기존 job 정보 조회 실패: {str(e)}")

        # 시작일과 종료일 문자열로 변환
        start_date_str = update_start_date.strftime("%Y-%m-%d")
        end_date_str = update_end_date.strftime("%Y-%m-%d") if update_end_date else "None"

        # 태그 및 설명 설정
        tags_str = f"['custom', '{owner}', 'start_date:{start_date_str}', 'title:{name}'"
        if end_date:
            tags_str += f", 'end_date:{end_date_str}'"
        tags_str += "]"

        enhanced_description = f"{update_description} (Start: {start_date_str})"
        if update_end_date:
            enhanced_description += f", End: {end_date_str}"

        # DAG 코드 생성
        dag_code = _generate_dag_code(
            dag_id, owner, update_start_date, update_end_date, success_emails, failure_emails,
            enhanced_description, update_schedule, tags_str, job_details
        )

        # 백업 파일 생성
        backup_file_path = f"{dag_file_path}.bak"
        try:
            if os.path.exists(dag_file_path):
                shutil.copy2(dag_file_path, backup_file_path)
                logger.info(f"Created backup at {backup_file_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup file: {str(e)}")

        # DAG 파일 저장
        with open(dag_file_path, 'w') as f:
            f.write(dag_code)
            logger.info(f"Updated DAG file at {dag_file_path}")

        # 메타데이터 파일 업데이트
        save_dag_metadata(
            dag_id=dag_id,
            job_ids=[str(job["id"]) for job in job_details],
            start_date=start_date_str,
            end_date=end_date_str if update_end_date else None,
            success_emails=success_emails,
            failure_emails=failure_emails
        )

        # 현재 DAG 상태 유지
        try:
            is_paused = current_dag.get("is_paused", False)
            toggle_dag_pause(dag_id, is_paused)
            logger.info(f"Maintained DAG pause state: is_paused={is_paused}")
        except Exception as e:
            logger.warning(f"Failed to update DAG state via API: {str(e)}")

        # 성공 로그
        logger.info(f"Successfully updated DAG: {dag_id}")
        return True

    except Exception as e:
        # 오류 발생 시 백업에서 복원 시도
        try:
            backup_file_path = f"/opt/airflow/dags/{dag_id}.py.bak"
            dag_file_path = f"/opt/airflow/dags/{dag_id}.py"

            if os.path.exists(backup_file_path):
                shutil.copy2(backup_file_path, dag_file_path)
                logger.info(f"Restored DAG file from backup after error: {str(e)}")
        except Exception as restore_error:
            logger.error(f"Failed to restore from backup: {str(restore_error)}")

        raise Exception(f"Failed to update DAG: {str(e)}")


def delete_dag(dag_id: str) -> bool:
    """DAG 삭제"""
    try:
        # API로 DAG 삭제
        endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}"

        response = requests.delete(
            endpoint,
            auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
        )

        # 파일 시스템에서도 삭제
        try:
            dag_file_path = f"/opt/airflow/dags/{dag_id}.py"
            meta_file_path = f"/opt/airflow/dags/{dag_id}.meta"

            if os.path.exists(dag_file_path):
                os.remove(dag_file_path)
                logger.info(f"Deleted DAG file: {dag_file_path}")

            if os.path.exists(meta_file_path):
                os.remove(meta_file_path)
                logger.info(f"Deleted metadata file: {meta_file_path}")
        except Exception as file_error:
            logger.warning(f"Failed to delete DAG files: {str(file_error)}")

        return response.status_code in (200, 204)
    except Exception as e:
        logger.error(f"Failed to delete DAG: {str(e)}")
        return False


def _generate_dag_code(
        dag_id: str,
        owner: str,
        start_date: datetime,
        end_date: Optional[datetime],
        success_emails: Optional[List[str]],
        failure_emails: Optional[List[str]],
        description: str,
        schedule_interval: str,
        tags: str,
        job_details: List[Dict[str, Any]]
) -> str:
    """DAG 코드 생성 (내부 헬퍼 함수)"""
    dag_code = f"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# START_DATE: {start_date.strftime("%Y-%m-%d")}
# END_DATE: {end_date.strftime("%Y-%m-%d") if end_date else "None"}

default_args = {{
    'owner': '{owner}',
    'depends_on_past': False,
    'start_date': datetime({start_date.year}, {start_date.month}, {start_date.day}),
    'end_date': {f"datetime({end_date.year}, {end_date.month}, {end_date.day})" if end_date else "None"},
    'email': [{', '.join([f"'{email}'" for email in (success_emails or [])])}],
    'email_on_failure': {bool(failure_emails or [])},
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}}

dag = DAG(
    '{dag_id}',
    default_args=default_args,
    description='{description}',
    schedule_interval='{schedule_interval}',
    tags={tags},
    catchup=False,
    is_paused_upon_creation=False
)
"""

    # 각 Job에 대한 Python 함수 정의
    for idx, job in enumerate(job_details):
        function_name = f"execute_job_{job['id']}"
        task_id = f"job_{job['id']}"

        # 코드에 들여쓰기 적용
        job_code = job['code'].rstrip()
        # 각 줄 앞에 4칸 들여쓰기 추가
        indented_code = "\n".join("    " + line for line in job_code.split("\n"))

        # Python 함수 정의
        dag_code += f"""
def {function_name}(**kwargs):
    # Job {job['id']} - {job['name']}
{indented_code}

task_{idx} = PythonOperator(
    task_id='{task_id}',
    python_callable={function_name},
    dag=dag,
)
"""

    # 태스크 의존성 설정 (순차 실행)
    if len(job_details) > 1:
        dag_code += "\n"
        for i in range(len(job_details) - 1):
            dag_code += f"task_{i} >> task_{i + 1}\n"

    return dag_code


def _save_dag_file(dag_id: str, dag_code: str) -> None:
    """DAG 파일 저장 (내부 헬퍼 함수)"""
    try:
        # 디렉토리 생성
        os.makedirs("/opt/airflow/dags", exist_ok=True)

        # DAG 파일 저장
        dag_file_path = f"/opt/airflow/dags/{dag_id}.py"
        with open(dag_file_path, 'w') as f:
            f.write(dag_code)
            logger.info(f"Saved DAG file at {dag_file_path}")
    except Exception as e:
        logger.error(f"Failed to save DAG file: {str(e)}")
        raise Exception(f"Failed to save DAG file: {str(e)}")