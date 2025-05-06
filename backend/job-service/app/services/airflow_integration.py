import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any

# Airflow API 설정
AIRFLOW_API_URL = os.environ.get('AIRFLOW_API_URL', 'http://airflow-webserver:8080/api/v1')
AIRFLOW_USERNAME = os.environ.get('AIRFLOW_USERNAME', 'airflow')
AIRFLOW_PASSWORD = os.environ.get('AIRFLOW_PASSWORD', 'airflow')
AIRFLOW_DAGS_FOLDER = os.environ.get('AIRFLOW__CORE__DAGS_FOLDER', '/opt/airflow/dags')

def create_schedule_dag(schedule_id: str, title: str, description: str, 
                       frequency: str, start_date: datetime, end_date: datetime, 
                       jobs: List[Dict[str, Any]], success_emails: List[str], 
                       failure_emails: List[str]) -> str:
    """
    스케줄 정보를 기반으로 Airflow DAG 파일 생성
    """
    try:
        # 스케줄 빈도를 Airflow cron 표현식으로 변환
        cron_expression = _convert_frequency_to_cron(frequency, start_date)
        
        # 이메일 설정
        success_emails_str = json.dumps(success_emails) if success_emails else "[]"
        failure_emails_str = json.dumps(failure_emails) if failure_emails else "[]"
        
        # DAG 파일 템플릿
        dag_template = f"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.email import send_email
from datetime import datetime, timedelta
import subprocess
import json
import sys
import os
import requests

# API 설정
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://job-service:8000/api')

def update_execution_status(schedule_id, status):
    '''스케줄 실행 상태 업데이트'''
    try:
        # 실제 API 호출로 상태 업데이트
        response = requests.post(
            f"{{API_BASE_URL}}/schedules/{{schedule_id}}/status",
            json={{"status": status}}
        )
        print(f"상태 업데이트 결과: {{response.status_code}}")
    except Exception as e:
        print(f"상태 업데이트 중 오류: {{e}}")
    
def send_success_email(context):
    '''성공 이메일 발송'''
    success_emails = {success_emails_str}
    if success_emails:
        send_email(
            to=success_emails,
            subject=f"[Success] Schedule {title} execution",
            html_content=f"Schedule <b>{title}</b> has been executed successfully at {{datetime.now().isoformat()}}."
        )
    
def send_failure_email(context):
    '''실패 이메일 발송'''
    failure_emails = {failure_emails_str}
    if failure_emails:
        send_email(
            to=failure_emails,
            subject=f"[Failed] Schedule {title} execution",
            html_content=f"Schedule <b>{title}</b> has failed to execute at {{datetime.now().isoformat()}}. Please check the logs."
        )

# DAG 기본 설정
default_args = {{
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.fromisoformat('{start_date.isoformat()}'),
    'email_on_failure': {bool(failure_emails)},
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_success_callback': send_success_email if {bool(success_emails)} else None,
    'on_failure_callback': send_failure_email if {bool(failure_emails)} else None
}}

# 종료 날짜 설정
{f"end_date = datetime.fromisoformat('{end_date.isoformat()}')" if end_date else "end_date = None"}

# DAG 정의
dag = DAG(
    '{schedule_id}',
    default_args=default_args,
    description='{description or title}',
    schedule_interval='{cron_expression}',
    catchup=False,
    end_date=end_date,
    tags=['auto-generated', 'job-service']
)

# 실행 시작 상태 업데이트
start_task = PythonOperator(
    task_id='update_start_status',
    python_callable=update_execution_status,
    op_kwargs={{'schedule_id': '{schedule_id}', 'status': 'running'}},
    dag=dag,
)
"""
        
        # 각 Job에 대한 Task 추가
        tasks = []
        for idx, job in enumerate(jobs):
            job_id = job['id']
            job_name = job['name']
            job_order = job['order']
            job_commands = job.get('commands', [])
            
            # Job 실행 함수 정의
            dag_template += f"""
def run_job_{job_id}():
    \"\"\"Job #{job_id}: {job_name} 실행\"\"\"
    try:
        print(f"Job {job_id} 실행 시작")
        
        # 데이터 로드 명령 실행
        if "{job.get('data_load_command', '')}":
            print(f"데이터 로드 명령 실행: {job.get('data_load_command', '')}")
            subprocess.run("{job.get('data_load_command', '')}", shell=True, check=True)
        
        # Python 코드 실행
        if "{job.get('code', '')}":
            print(f"Python 코드 실행")
            # 코드 길이가 너무 길어 템플릿에 직접 넣기 어려우므로
            # 실제 구현에서는 별도 파일로 저장하거나 다른 방법 사용 필요
            # exec('''{job.get('code', '')}''')
            
            # API를 통해 코드 실행
            response = requests.post(
                f"{{API_BASE_URL}}/jobs/{job_id}/execute",
                json={{}}
            )
            if response.status_code != 200:
                raise Exception(f"코드 실행 API 호출 실패: {{response.status_code}}")
            
        # 추가 명령어 실행
        commands = {json.dumps([cmd.get('content', '') for cmd in job_commands])}
        for cmd in commands:
            print(f"명령어 실행: {{cmd}}")
            subprocess.run(cmd, shell=True, check=True)
            
        print(f"Job {job_id} 실행 완료")
        return True
    except Exception as e:
        print(f"Job {job_id} 실행 중 오류: {{e}}")
        raise
        
# Job {job_id} 실행 Task
job_{job_id}_task = PythonOperator(
    task_id='run_job_{job_id}',
    python_callable=run_job_{job_id},
    dag=dag,
)
"""
            tasks.append(f"job_{job_id}_task")
        
        # 작업 완료 후 상태 업데이트
        dag_template += f"""
# 실행 완료 상태 업데이트
end_task = PythonOperator(
    task_id='update_end_status',
    python_callable=update_execution_status,
    op_kwargs={{'schedule_id': '{schedule_id}', 'status': 'success'}},
    dag=dag,
)

# 작업 순서 정의
start_task"""

        # 작업 순서 Chain 정의 (Airflow 2.0+ 문법)
        for task in tasks:
            dag_template += f" >> {task}"
        
        dag_template += " >> end_task"
        
        # DAG 파일 저장
        dag_file_path = os.path.join(AIRFLOW_DAGS_FOLDER, f"{schedule_id}.py")
        with open(dag_file_path, 'w') as f:
            f.write(dag_template)
        
        # Airflow API를 통해 DAG 등록 또는 갱신
        _refresh_dag_api(schedule_id)
        
        return schedule_id
    except Exception as e:
        print(f"DAG 생성 중 오류 발생: {e}")
        raise Exception(f"Airflow DAG 생성 실패: {str(e)}")

def update_schedule_dag(schedule_id: str, title: str, description: str, 
                       frequency: str, start_date: datetime, end_date: datetime, 
                       jobs: List[Dict[str, Any]], success_emails: List[str], 
                       failure_emails: List[str]) -> str:
    """
    스케줄 정보 업데이트를 기반으로 Airflow DAG 파일 갱신
    """
    try:
        # 기존 DAG 파일 삭제
        delete_schedule_dag(schedule_id)
        
        # 새 DAG 파일 생성
        return create_schedule_dag(
            schedule_id, title, description, frequency, 
            start_date, end_date, jobs, success_emails, failure_emails
        )
    except Exception as e:
        print(f"DAG 업데이트 중 오류 발생: {e}")
        raise Exception(f"Airflow DAG 업데이트 실패: {str(e)}")

def delete_schedule_dag(schedule_id: str) -> bool:
    """
    Airflow DAG 파일 삭제
    """
    try:
        dag_file_path = os.path.join(AIRFLOW_DAGS_FOLDER, f"{schedule_id}.py")
        if os.path.exists(dag_file_path):
            os.remove(dag_file_path)
            
            # Airflow API를 통해 DAG 비활성화
            _pause_dag_api(schedule_id)
            
        return True
    except Exception as e:
        print(f"DAG 삭제 중 오류 발생: {e}")
        raise Exception(f"Airflow DAG 삭제 실패: {str(e)}")

def _convert_frequency_to_cron(frequency: str, start_time: datetime) -> str:
    """
    스케줄 빈도를 Airflow cron 표현식으로 변환
    """
    minute = start_time.minute
    hour = start_time.hour
    
    if frequency == "daily":
        return f"{minute} {hour} * * *"
    elif frequency == "weekly":
        # 시작일의 요일을 사용 (0: 월요일, 6: 일요일)
        day_of_week = start_time.weekday()
        return f"{minute} {hour} * * {day_of_week}"
    elif frequency == "monthly":
        # 시작일의 일을 사용
        day = start_time.day
        return f"{minute} {hour} {day} * *"
    elif frequency == "yearly":
        # 시작일의 월과 일을 사용
        month = start_time.month
        day = start_time.day
        return f"{minute} {hour} {day} {month} *"
    elif frequency.startswith("cron:"):
        # 사용자 정의 cron 표현식
        return frequency[5:].strip()
    else:
        # 기본값: 매일
        return f"{minute} {hour} * * *"

def _refresh_dag_api(dag_id: str):
    """
    Airflow REST API를 통해 특정 DAG 갱신
    """
    try:
        # 먼저 DAG가 존재하는지 확인
        check_response = requests.get(
            f"{AIRFLOW_API_URL}/dags/{dag_id}",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"}
        )
        
        if check_response.status_code == 404:
            # DAG가 아직 로드되지 않았으면 새로고침 진행
            refresh_response = requests.post(
                f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns",
                auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
                headers={"Content-Type": "application/json"},
                json={"dag_run_id": "manual_refresh"}
            )
            if refresh_response.status_code not in [200, 201]:
                print(f"DAG 새로고침 실패: {refresh_response.status_code}")
            else:
                # DAG 활성화
                _unpause_dag_api(dag_id)
        else:
            print(f"DAG {dag_id} 이미 존재함")
            # 이미 존재하는 경우에도 활성화 확인
            _unpause_dag_api(dag_id)
    except Exception as e:
        print(f"DAG API 호출 중 오류 발생: {e}")

def _unpause_dag_api(dag_id: str):
    """
    Airflow REST API를 통해 DAG 활성화
    """
    try:
        response = requests.patch(
            f"{AIRFLOW_API_URL}/dags/{dag_id}",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"},
            json={"is_paused": False}
        )
        if response.status_code != 200:
            print(f"DAG 활성화 실패: {response.status_code}")
        else:
            print(f"DAG {dag_id} 활성화 성공")
    except Exception as e:
        print(f"DAG 활성화 중 오류 발생: {e}")

def _pause_dag_api(dag_id: str):
    """
    Airflow REST API를 통해 DAG 비활성화
    """
    try:
        response = requests.patch(
            f"{AIRFLOW_API_URL}/dags/{dag_id}",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"},
            json={"is_paused": True}
        )
        if response.status_code != 200:
            print(f"DAG 비활성화 실패: {response.status_code}")
        else:
            print(f"DAG {dag_id} 비활성화 성공")
    except Exception as e:
        print(f"DAG 비활성화 중 오류 발생: {e}")