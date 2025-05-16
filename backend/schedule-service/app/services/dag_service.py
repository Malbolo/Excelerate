from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import ulid
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.log_config import logger
from app.services.airflow_client import airflow_client
from app.utils import date_utils, cron_utils, log_utils
from app.core import auth
from app.db import database
from app.crud import schedule_crud

class DagService:
    """DAG 관련 서비스 클래스"""

    @staticmethod
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
            user_id: int = None,
            db: Session = None,
    ) -> str:
        """새로운 DAG를 생성합니다."""
        close_db = False
        if db is None:
            db = next(database.get_db())
            close_db = True

        try:
            # DAG ID는 고유해야 함
            # DAG ID는 userid_time 형식으로 생성 (밀리초까지 포함하여 추가 고유성 확보)
            timestamp = date_utils.get_now_utc().strftime('%Y%m%d%H%M%S%f')[:18]
            dag_id = f"dag_{ulid.ULID().str}"

            # Job Service에서 job 정보 가져오기
            job_details = DagService._get_job_basic_info(job_ids, user_id)

            # 시작일과 종료일 문자열로 변환
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "None"

            # 태그 및 설명 설정
            tags = [f'owner:{owner}', f'start_date:{start_date_str}', f'title:{name}']
            if end_date:
                tags.append(f'end_date:{end_date_str}')
            tags_str = str(tags)

            # DAG 코드 생성
            dag_code = DagService._generate_dag_code(
                dag_id, owner, start_date, end_date, success_emails, failure_emails,
                description, cron_expression, tags_str, job_details, name
            )

            # DAG 파일 저장
            DagService._save_dag_file(dag_id, dag_code)

            schedule_data = {
                "title": name,
                "description": description,
                "cron_expression": cron_expression,
                "frequency": cron_utils.convert_cron_to_frequency(cron_expression),
                "execution_time": execution_time,
                "start_date": start_date,
                "end_date": end_date,
                "success_emails": success_emails or [],
                "failure_emails": failure_emails or [],
                "owner": owner,
                "job_ids": job_ids
            }

            schedule_crud.create_schedule(db, dag_id, schedule_data, user_id)

            return dag_id

        except Exception as e:
            logger.error(f"Error creating DAG: {str(e)}")
            raise Exception(f"DAG 생성에 실패했습니다: {str(e)}")

        finally:
            if close_db:
                db.close()

    @staticmethod
    def update_dag(
            dag_id: str,
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
            user_id: int = None,
            db: Session = None
    ) -> bool:
        """기존 DAG 업데이트 - 동일한 DAG ID를 유지하면서 내용만 교체"""
        close_db = False
        if db is None:
            db = next(database.get_db())
            close_db = True

        try:
            # 기존 DAG 정보 조회
            current_dag = airflow_client.get_dag_detail(dag_id)
            dag_file_path = os.path.join(settings.AIRFLOW_DAGS_PATH, f"{dag_id}.py")

            # Job 상세 정보 조회
            job_details = DagService._get_job_basic_info(job_ids, user_id)

            # 시작일과 종료일 문자열로 변환
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "None"

            # 태그 및 설명 설정
            tags = [f'owner:{owner}', f'start_date:{start_date_str}', f'title:{name}']
            if end_date:
                tags.append(f'end_date:{end_date_str}')
            tags_str = str(tags)

            # DAG 코드 생성
            dag_code = DagService._generate_dag_code(
                dag_id, owner, start_date, end_date, success_emails, failure_emails,
                description, cron_expression, tags_str, job_details, name
            )

            # DAG 파일 저장
            with open(dag_file_path, 'w') as f:
                f.write(dag_code)
                logger.info(f"Updated DAG file at {dag_file_path}")

            frequency = cron_utils.convert_cron_to_frequency(cron_expression)

            schedule_crud.update_schedule_metadata(
                db,
                dag_id=dag_id,
                data={
                    "job_ids": [str(job["id"]) for job in job_details],
                    "start_date": start_date,
                    "end_date": end_date,
                    "success_emails": success_emails or [],
                    "failure_emails": failure_emails or [],
                    "title": name,
                    "description": description,
                    "cron_expression": cron_expression,
                    "frequency": frequency,
                    "execution_time": execution_time,
                    "owner": owner
                }
            )

            # 현재 DAG 상태 유지
            try:
                is_paused = current_dag.get("is_paused", False)
                airflow_client.toggle_dag_pause(dag_id, is_paused)
                logger.info(f"Maintained DAG pause state: is_paused={is_paused}")
            except Exception as e:
                logger.warning(f"Failed to update DAG state via API: {str(e)}")

            # 성공 로그
            logger.info(f"Successfully updated DAG: {dag_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating DAG: {str(e)}")
            raise Exception(f"Failed to update DAG: {str(e)}")

        finally:
            if close_db:
                db.close()

    @staticmethod
    def delete_dag(dag_id: str) -> bool:
        """DAG 삭제"""
        try:
            # API로 DAG 삭제
            airflow_client.delete_dag(dag_id)

            # 파일 시스템에서도 삭제
            try:
                dag_file_path = os.path.join(settings.AIRFLOW_DAGS_PATH, f"{dag_id}.py")

                # Python 파일 삭제
                if os.path.exists(dag_file_path):
                    os.remove(dag_file_path)
                    logger.info(f"Deleted DAG file: {dag_file_path}")

            except Exception as file_error:
                logger.warning(f"Failed to delete DAG files: {str(file_error)}")

            return True
        except Exception as e:
            logger.error(f"Failed to delete DAG: {str(e)}")
            return False

    @staticmethod
    def _get_job_basic_info(job_ids: List[str], user_id: int) -> List[Dict[str, Any]]:
        """Job Service API를 통해 job 정보 가져오기"""
        job_service_url = settings.JOB_SERVICE_URL
        if not job_service_url:
            raise Exception("JOB_SERVICE_URL 환경 변수가 설정되지 않았습니다.")

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

            return job_details

        except Exception as e:
            raise Exception(f"Job 정보 조회 중 오류 발생: {str(e)}")

    @staticmethod
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
            job_details: List[Dict[str, Any]],
            name: str
    ) -> str:
        """DAG 코드 생성 (내부 헬퍼 함수)"""
        dag_code = f"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule

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

# 성공 이메일 콜백 함수
def send_success_email(**kwargs):
    \"\"\"DAG 성공 시 이메일 전송\"\"\"
    success_to = {success_emails!r} 
    if not success_to:
        return
        
    dag_run = kwargs['dag_run']
    dag_id = dag_run.dag_id
    
    email = EmailOperator(
        task_id='send_success_email',
        to=success_to,  
        subject=f"[성공] {name} (DAG ID: {dag_id})",
        html_content='''
        <h3>DAG {{ dag_run.dag_id }} 실행이 성공적으로 완료되었습니다.</h3>
        <p>DAG 이름: {name}</p>
        <p>실행 날짜: {{ ds }}</p>
        <p>실행 시간: {{ execution_date }}</p>
        ''',
        dag=kwargs['dag']
    )
    email.execute(context=kwargs)

# 실패 이메일 콜백 함수
def send_failure_email(**kwargs):
    \"\"\"DAG 실패 시 이메일 전송\"\"\"
    failure_to = {failure_emails!r}
    if not failure_to:
        return
        
    dag_run = kwargs['dag_run']
    dag_id = dag_run.dag_id
    
    email = EmailOperator(
        task_id='send_failure_email',
        to=failure_to, 
        subject=f"[실패] {name} (DAG ID: {dag_id})",
        html_content='''
        <h3>DAG {{ dag_run.dag_id }} 실행이 실패했습니다.</h3>
        <p>DAG 이름: {name}</p>
        <p>실행 날짜: {{ ds }}</p>
        <p>실행 시간: {{ execution_date }}</p>
        <p>실패한 작업: {{ task_instance.task_id }}</p>
        ''',
        dag=kwargs['dag']
    )
    email.execute(context=kwargs)
    
default_args = {{
    'owner': '{owner}',
    'depends_on_past': False,
    'email': [{', '.join([f"'{email}'" for email in (success_emails or [])])}],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    # 'retry_delay': timedelta(seconds=1),
}}

dag = DAG(
    '{dag_id}',
    default_args=default_args,
    dag_display_name='{name}',
    description='{description}',
    schedule_interval='{schedule_interval}',
    start_date= datetime({start_date.year}, {start_date.month}, {start_date.day}),
    end_date= {f"datetime({end_date.year}, {end_date.month}, {end_date.day})" if end_date else "None"},
    tags={tags},
    catchup=False,
    is_paused_upon_creation=False,
    on_success_callback=send_success_email if {bool(success_emails)} else None,
    on_failure_callback=send_failure_email if {bool(failure_emails)} else None
)
"""

        # 각 Job에 대한 Python 함수 정의
        for idx, job in enumerate(job_details):
            function_name = f"execute_job_{job['id']}"
            task_id = f"job_{job['id']}"
            branch_id = f"check_email_{job['id']}"
            skip_id = f"skip_email_{job['id']}"
            email_id = f"email_job_{job['id']}"

            # data_load_code 체크
            if job.get("data_load_code"):
                data_load_code = job['data_load_code'].rstrip()
                indented_data_code = "\n".join("    " + line for line in data_load_code.split("\n"))
                has_code = True
            else:
                indented_data_code = ""
                has_code = False

            # 코드에 들여쓰기 적용
            job_code = job['code'].rstrip()
            indented_code = "\n".join("    " + line for line in job_code.split("\n"))

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
    trigger_rule=TriggerRule.NONE_FAILED,
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
                dag_code += f"task_{i}_cleanup >> task_{i + 1}\n"

        return dag_code

    @staticmethod
    def _save_dag_file(dag_id: str, dag_code: str) -> None:
        """DAG 파일 저장 (내부 헬퍼 함수)"""
        try:
            # 디렉토리 생성
            os.makedirs(settings.AIRFLOW_DAGS_PATH, exist_ok=True)

            # DAG 파일 저장
            dag_file_path = os.path.join(settings.AIRFLOW_DAGS_PATH, f"{dag_id}.py")
            with open(dag_file_path, 'w') as f:
                f.write(dag_code)
                logger.info(f"Saved DAG file at {dag_file_path}")
        except Exception as e:
            logger.error(f"Failed to save DAG file: {str(e)}")
            raise Exception(f"Failed to save DAG file: {str(e)}")