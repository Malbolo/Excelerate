import os
import shutil
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.core.log_config import logger
# from app.db.database import get_db
from app.services.dag_query import get_dag_detail
from app.services.execution import toggle_dag_pause
from app.services.metadata import save_dag_metadata, get_dag_metadata
from app.core import auth

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
        execution_time: str = None,
        user_id: int = None
) -> str:
    """새로운 DAG를 생성합니다."""
    # DAG ID는 고유해야 함
    # DAG ID는 userid_time 형식으로 생성 (밀리초까지 포함하여 추가 고유성 확보)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:18]  # 년월일시분초밀리초(3자리)
    dag_id = f"{owner}_{timestamp}"

    try:
        # Job Service URL 가져오기
        job_service_url = os.getenv("JOB_SERVICE_URL")
        if not job_service_url:
            raise Exception("JOB_SERVICE_URL 환경 변수가 설정되지 않았습니다.")

        # Job Service API를 통해 job 정보 가져오기
        try:
            # auth.py의 함수 사용하여 API 호출
            response = auth.call_service_api(
                service_url=job_service_url,
                method="POST",
                endpoint="/api/jobs/for-schedule",
                data={"job_ids": [str(job_id) for job_id in job_ids]},
                user_id=user_id
            )

            if not response or "jobs" not in response:
                raise Exception("Job 정보를 가져오지 못했습니다.")

            # 응답에서 job 정보 추출하여 job_details 구성
            job_details = []
            job_details_map = {}

            # 배열을 딕셔너리로 변환
            for job in response["jobs"]:
                job_id = job.get("id")
                if job_id:
                    job_details_map[job_id] = job

            # job_ids 순서에 맞게 job_details 배열 구성
            for job_id in job_ids:
                job_info = job_details_map.get(str(job_id))
                if not job_info:
                    raise Exception(f"Job ID {job_id}를 찾을 수 없습니다.")

                job_details.append({
                    "id": job_id,
                    "name": job_info.get("title", f"Job {job_id}"),
                    "code": job_info.get("code", ""),
                    "data_load_url": job_info.get("data_load_url", ""),
                    "data_load_code": job_info.get("data_load_code", "")
                })

        except Exception as e:
            raise Exception(f"Job 정보 조회 중 오류 발생: {str(e)}")

        # 시작일과 종료일 문자열로 변환
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "None"

        # 태그 및 설명 설정
        tags_str = f"['custom', '{owner}', 'start_date:{start_date_str}', 'title:{name}'"
        if end_date:
            tags_str += f", 'end_date:{end_date_str}'"
        tags_str += "]"

        enhanced_description = f"{description}"

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

    except Exception as e:
        logger.error(f"Error creating DAG: {str(e)}")
        raise Exception(f"DAG 생성에 실패했습니다: {str(e)}")

def update_dag(
        dag_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        cron_expression: Optional[str] = None,
        job_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success_emails: Optional[List[str]] = None,
        failure_emails: Optional[List[str]] = None,
        user_id: int = None
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

        # Job Service URL 가져오기
        job_service_url = os.getenv("JOB_SERVICE_URL")
        if not job_service_url:
            raise Exception("JOB_SERVICE_URL 환경 변수가 설정되지 않았습니다.")

        # job 정보 가져오기
        job_details = []
        if not job_ids:
            # job_ids가 제공되지 않은 경우 - 오류 발생
            raise Exception("스케줄 업데이트에는 최소 하나 이상의 Job ID가 필요합니다.")

        # 새로운 job ID 목록이 제공된 경우 - Job Service API 호출
        try:
            # auth.py의 함수 사용하여 API 호출
            job_data_response = auth.call_service_api(
                service_url=job_service_url,
                method="POST",
                endpoint="/api/jobs/for-schedule",
                data={"job_ids": [str(job_id) for job_id in job_ids]},
                user_id=user_id
            )

            # 응답 로깅 (디버깅용)
            logger.debug(f"Job Service API 응답: {job_data_response}")

            # 응답 형식 확인 및 처리
            if not job_data_response or "jobs" not in job_data_response:
                raise Exception("Job 정보를 가져오지 못했습니다.")

            # 배열을 딕셔너리로 변환
            job_details_map = {}
            for job in job_data_response["jobs"]:
                job_id = job.get("id")
                if job_id:
                    job_details_map[job_id] = job

            # job_ids 순서에 맞게 job_details 배열 구성
            for job_id in job_ids:
                job_info = job_details_map.get(str(job_id))
                if not job_info:
                    raise Exception(f"Job ID {job_id}를 찾을 수 없습니다.")

                job_details.append({
                    "id": job_id,
                    "name": job_info.get("title", f"Job {job_id}"),
                    "code": job_info.get("code", ""),
                    "data_load_url": job_info.get("data_load_url", ""),
                    "data_load_code": job_info.get("data_load_code", "")
                })
        except Exception as e:
            logger.error(f"Job 정보 조회 중 오류 발생: {str(e)}")
            raise Exception(f"Job 정보 조회 중 오류 발생: {str(e)}")

        # 시작일과 종료일 문자열로 변환
        start_date_str = update_start_date.strftime("%Y-%m-%d")
        end_date_str = update_end_date.strftime("%Y-%m-%d") if update_end_date else "None"

        # 태그 및 설명 설정
        tags_str = f"['custom', '{owner}', 'start_date:{start_date_str}', 'title:{update_name}'"
        if update_end_date:
            tags_str += f", 'end_date:{end_date_str}'"
        tags_str += "]"

        enhanced_description = f"{update_description}"

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
            start_date=update_start_date.isoformat(),
            end_date=update_end_date.isoformat() if update_end_date else None,
            success_emails=success_emails,
            failure_emails=failure_emails,
            title=update_name,
            description=update_description
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
from airflow.operators.email import EmailOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator

from datetime import datetime, timedelta

import requests
import shutil
from tempfile import mkdtemp
import pandas as pd
import os
import re

from utils.minio_client import MinioClient
from utils.code_util import insert_df_to_excel

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
    'retry_delay': timedelta(seconds=1),
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
        branch_id = f"check_email_{job['id']}"
        skip_id   = f"skip_email_{job['id']}"
        email_id = f"email_job_{job['id']}"

        # data_load_code 체크
        if job.get("data_load_code"):
            data_load_code = job['data_load_code'].rstrip()
            indented_data_code = "\n".join("        " + line for line in data_load_code.split("\n"))
            has_code = True
        else:
            indented_data_code = ""
            has_code = False

        # 코드에 들여쓰기 적용
        job_code = job['code'].rstrip()
        # 각 줄 앞에 4칸 들여쓰기 추가
        indented_code = "\n".join("    " + line for line in job_code.split("\n"))

        # Python 함수 정의
        dag_code += f"""
def {function_name}(**kwargs):
    # Job {job['id']} - {job['name']}

    # 0) url 날짜 변환
    url = "{job['data_load_url']}"
    
    if {has_code}:
{indented_data_code}
        # 기존 URL의 start_date=, end_date=값 교체
        if startdate:
            url = re.sub(r"(start_date=)[^&]+", "\\\\1" + startdate, url)
        if enddate:
            url = re.sub(r"(end_date=)[^&]+", "\\\\1" + enddate, url)

    # 1) 데이터 로드
    resp = requests.get(url)
    resp.raise_for_status()
    raw = resp.json()
    df = pd.DataFrame(raw["data"])

    out = None

    # 2) 사용자 코드 실행 (df 조작)
{indented_code}

    # 3) 엑셀 파일 경로 리턴 (임시 파일) 
    return out

# 4) PythonOperator: 데이터 처리 
task_{idx} = PythonOperator(
    task_id='{task_id}',
    python_callable={function_name},
    dag=dag,
)

# 5) 브랜치 태스크
def branch_email_{job['id']}(**kwargs):
    path = kwargs['ti'].xcom_pull(task_ids='{task_id}')
    # out 이 None 이거나 빈 문자열이면 스킵
    if path:
        return '{email_id}'
    else:
        return '{skip_id}'

task_{idx}_branch = BranchPythonOperator(
    task_id='{branch_id}',
    python_callable=branch_email_{job['id']},
    dag=dag,
)

# 6) EmailOperator: 결과 전송 
task_{idx}_email = EmailOperator( 
    task_id="{email_id}", 
    to={success_emails!r}, 
    subject="Job {job['id']} 결과", 
    html_content=f"Job {job['id']} 실행 결과를 첨부합니다.", 
    files=["{{{{ ti.xcom_pull(task_ids='{task_id}') }}}}"], 
    dag=dag, 
)

# 7) 건너뛰기용 더미 태스크
task_{idx}_skip = DummyOperator(
    task_id='{skip_id}',
    dag=dag,
)
 
# 8) 의존성 설정 
task_{idx} >> task_{idx}_branch
task_{idx}_branch >> task_{idx}_email
task_{idx}_branch >> task_{idx}_skip

# 9) Cleanup 태스크 정의 (run→branch→email 후 실행)
def cleanup_file_{job['id']}(**kwargs):
    # run_job 태스크에서 반환한 out 경로
    path = kwargs['ti'].xcom_pull(task_ids='{task_id}')
    if path and os.path.exists(path):
        workdir = os.path.dirname(path)
        # 디렉터리가 존재하면 통째로 삭제
        if os.path.isdir(workdir):
            shutil.rmtree(workdir)

task_{idx}_cleanup = PythonOperator(
    task_id='cleanup_job_{job['id']}',
    python_callable=cleanup_file_{job['id']},
    # email 또는 skip 이후에 무조건 실행되도록
    trigger_rule='all_done',
    dag=dag,
)

# 10) 의존성 연결
task_{idx}_email   >> task_{idx}_cleanup
task_{idx}_skip    >> task_{idx}_cleanup
"""

    # 태스크 의존성 설정 (순차 실행)
    if len(job_details) > 1:
        dag_code += "\n"
        for i in range(len(job_details) - 1):
            dag_code += f"task_{i}_cleanup >> task_{i+1}\n"

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