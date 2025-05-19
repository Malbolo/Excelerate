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
            dag_id = ulid.ULID()

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

            schedule_crud.create_schedule(db, id=dag_id, data=schedule_data, user_id=user_id)

            return str(dag_id)

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
        """
        기존 DAG 업데이트 - Airflow에서는 삭제 후 재생성, DB에서는 업데이트
        """
        close_db = False
        if db is None:
            db = next(database.get_db())
            close_db = True

        try:
            # 1. Airflow에서만 DAG 삭제 (DB는 유지)
            try:
                DagService.delete_dag(dag_id, db, delete_from_db=False)
            except Exception as e:
                logger.warning(f"Error during DAG cleanup: {str(e)}")

            # 2. Job 상세 정보 조회
            job_details = DagService._get_job_basic_info(job_ids, user_id)

            # 3. 새 DAG 파일 생성 (기존 ID 유지)
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

            # 4. DB에서 스케줄 정보 업데이트 (삭제하지 않음)
            frequency = cron_utils.convert_cron_to_frequency(cron_expression)

            # CRUD 함수 사용하여 업데이트
            updated = schedule_crud.update_schedule(
                db,
                id=dag_id,
                data={
                    "job_ids": job_ids,
                    "start_date": start_date,
                    "end_date": end_date,
                    "success_emails": success_emails,
                    "failure_emails": failure_emails,
                    "title": name,
                    "description": description,
                    "cron_expression": cron_expression,
                    "frequency": frequency,
                    "execution_time": execution_time,
                    "owner": owner
                }
            )

            if not updated:
                logger.warning(f"Failed to update schedule in DB: {dag_id}")
            else:
                logger.info(f"Updated schedule in DB: {dag_id}")

            return True

        except Exception as e:
            logger.error(f"Error updating DAG: {str(e)}")
            raise Exception(f"Failed to update DAG: {str(e)}")

        finally:
            if close_db and db is not None:
                db.close()

    @staticmethod
    def delete_dag(dag_id: str, db: Session = None, delete_from_db: bool = True) -> bool:
        """
        DAG 삭제

        Args:
            dag_id: 삭제할 DAG ID
            db: 데이터베이스 세션
            delete_from_db: DB에서도 삭제할지 여부
        """
        close_db = False
        if db is None and delete_from_db:
            db = next(database.get_db())
            close_db = True

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

            # DB에서 스케줄 삭제
            if delete_from_db:
                try:
                    schedule_crud.delete_schedule(db, dag_id)
                    logger.info(f"Deleted schedule from DB: {dag_id}")
                except Exception as db_error:
                    logger.warning(f"Failed to delete schedule from DB: {str(db_error)}")

            return True
        except Exception as e:
            logger.error(f"Failed to delete DAG: {str(e)}")
            return False
        finally:
            if close_db and db is not None:
                db.close()

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
from airflow.utils.email import send_email

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

# DAG 상태 알림 함수 - 항상 이메일 발송
def notify_dag_status(**kwargs):
    '''DAG 실행 완료 시 이메일 전송'''
    dag_run = kwargs['dag_run']
    ti_list = dag_run.get_task_instances()
    failed_tasks = [ti for ti in ti_list if ti.state == 'failed']
    
    # 실행 날짜와 시간 가져오기
    ds = kwargs.get('ds', '')
    execution_date = kwargs.get('execution_date', '')
    
    if failed_tasks:
        # 실패한 태스크가 있으면 실패 이메일 발송
        failed_task_names = [ti.task_id for ti in failed_tasks]
        send_email(
            to={failure_emails!r},
            subject=f"[실패] {name} (DAG ID: {{dag_run.dag_id}})",
            html_content=f'''
            <h3>DAG {{dag_run.dag_id}} 실행이 실패했습니다.</h3>
            <p>DAG 이름: {name}</p>
            <p>실패한 태스크: {{', '.join(failed_task_names)}}</p>
            <p>실행 날짜: {{ds}}</p>
            <p>실행 시간: {{execution_date}}</p>
            '''
        )
    else:
        # 모든 태스크가 성공 또는 스킵되었으면 성공 이메일 발송
        send_email(
            to={success_emails!r},
            subject=f"[성공] {name} (DAG ID: {{dag_run.dag_id}})",
            html_content=f'''
            <h3>DAG {{dag_run.dag_id}} 실행이 성공적으로 완료되었습니다.</h3>
            <p>DAG 이름: {name}</p>
            <p>실행 날짜: {{ds}}</p>
            <p>실행 시간: {{execution_date}}</p>
            '''
        )

def fail_task(**kwargs):
    '''이 함수는 항상 실패하도록 예외를 발생시킵니다'''
    raise Exception("이전 태스크 중 실패한 태스크가 감지되었습니다.")

# DAG 설정
default_args = {{
    'depends_on_past': False,
    'owner' : '{owner}',
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
    is_paused_upon_creation=False
    # 콜백 함수 대신 최종 알림 태스크 사용
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
                indented_data_code = "\n".join("        " + line for line in data_load_code.split("\n"))
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
            url = re.sub(r'(?<=start_date=)[^&]+', startdate, url)
        if enddate:
            url = re.sub(r'(?<=end_date=)[^&]+',   enddate,   url)

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

        # 마지막에 최종 상태 알림 태스크 추가
        last_idx = len(job_details) - 1
        dag_code += f"""
# 실패 감지 태스크 (하나라도 실패했을 때)
failure_sensor_task = PythonOperator(
    task_id='failure_sensor',
    python_callable=fail_task,  
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag,
)

# 성공/실패 상관없이 실행되는 알림 태스크
notification_task = PythonOperator(
    task_id='send_notification',
    python_callable=notify_dag_status,  # 기존 notify_dag_status 함수 사용 (상태에 따라 분기)
    trigger_rule=TriggerRule.ALL_DONE,  # 모든 선행 태스크가 완료되면 실행
    dag=dag,
)

# 마지막 cleanup 태스크와 연결
task_{last_idx}_cleanup >> failure_sensor_task
task_{last_idx}_cleanup >> notification_task
"""

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