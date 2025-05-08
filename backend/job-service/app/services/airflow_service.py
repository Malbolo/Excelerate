import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import calendar
import os
from croniter import croniter
from app.db.database import get_db
from app.models.models import Job, JobCommand
from app.crud import crud

class Settings:
    AIRFLOW_API_URL: str = os.getenv("AIRFLOW_API_URL")
    AIRFLOW_USERNAME: str = os.getenv("AIRFLOW_USERNAME")
    AIRFLOW_PASSWORD: str = os.getenv("AIRFLOW_PASSWORD")

settings = Settings()

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
    # DAG ID는 고유해야 함
    dag_id = f"{owner}_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # MySQL에서 job 정보 가져오기
    db = next(get_db())
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
    tags_str = f"['custom', '{owner}', 'start_date:{start_date_str}'"
    if end_date:
        tags_str += f", 'end_date:{end_date_str}'"
    tags_str += "]"

    enhanced_description = f"{description} (Start: {start_date_str})"
    if end_date:
        enhanced_description += f", End: {end_date_str}"

    # DAG 코드 생성
    dag_code = f"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# START_DATE: {start_date_str}
# END_DATE: {end_date_str if end_date else "None"}

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
    description='{enhanced_description}',
    schedule_interval='{cron_expression}',
    tags={tags_str},
    catchup=False,
    is_paused_upon_creation=False
)
"""

    # 각 Job에 대한 Python 함수 정의
    for idx, job in enumerate(job_details):
        function_name = f"execute_job_{job['id']}"
        task_id = f"job_{job['id']}"

        # 코드에 들여쓰기 적용 (수정된 부분)
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

    # DAG 파일 저장
    try:
        # 디렉토리 생성
        import os
        os.makedirs("/opt/airflow/dags", exist_ok=True)

        # DAG 파일 저장
        dag_file_path = f"/opt/airflow/dags/{dag_id}.py"
        with open(dag_file_path, 'w') as f:
            f.write(dag_code)

        # 메타데이터 파일 생성
        meta_file_path = f"/opt/airflow/dags/{dag_id}.meta"
        with open(meta_file_path, 'w') as f:
            f.write(f"JOBS:{','.join(job_ids)}\n")
            f.write(f"START_DATE:{start_date.isoformat()}\n")
            if end_date:
                f.write(f"END_DATE:{end_date.isoformat()}\n")
            else:
                f.write("END_DATE:None\n")
            f.write(f"SUCCESS_EMAILS:{','.join(success_emails or [])}\n")
            f.write(f"FAILURE_EMAILS:{','.join(failure_emails or [])}\n")
            f.write(f"EXECUTION_TIME:{execution_time}\n")

    except Exception as e:
        raise Exception(f"Failed to create DAG file: {str(e)}")

    return dag_id

def get_dags_by_owner(owner: str) -> List[Dict[str, Any]]:
    """특정 소유자(owner)의 DAG 목록 조회"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags"
    params = {
        "tags": owner,
        "limit": 100  # 필요에 따라 조정
    }
    
    response = requests.get(
        endpoint,
        params=params,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get DAGs: {response.text}")
    
    return response.json().get("dags", [])

def get_all_dags(limit: int = 200) -> List[Dict[str, Any]]:
    """모든 DAG 목록 조회 (소유자 필터 없이)"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags"
    params = {
        "limit": limit
    }

    response = requests.get(
        endpoint,
        params=params,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get all DAGs: {response.text}")

    return response.json().get("dags", [])

def build_monthly_dag_calendar(dags: List[Dict[str, Any]], year: int, month: int) -> List[Dict[str, Any]]:
    """
    월별 DAG 실행 통계 생성 (pending 포함: 예상 실행일 기준)

    참고: 활성 상태인 DAG만 처리하며, DAG의 시작일 이후 날짜만 고려합니다.
    """
    # 타임존을 명시적으로 설정 (UTC 사용)
    first_day = datetime(year, month, 1, tzinfo=timezone.utc)
    _, last_day_num = calendar.monthrange(year, month)
    last_day = datetime(year, month, last_day_num, 23, 59, 59, tzinfo=timezone.utc)

    # 현재 날짜
    now = datetime.now(timezone.utc)

    # 월의 모든 날짜를 미리 딕셔너리로 초기화
    all_days = []
    for day in range(1, last_day_num + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        all_days.append({
            "date": date_str,
            "total": 0,
            "success": 0,
            "failed": 0,
            "pending": 0
        })

    # 날짜별 데이터 인덱스 구성 (빠른 조회용)
    date_index = {item["date"]: i for i, item in enumerate(all_days)}

    # DAG 별로 처리
    for dag in dags:
        # DAG 활성 상태 확인 - 비활성 DAG는 건너뜁니다
        is_paused = dag.get("is_paused", False)
        if is_paused:
            continue

        dag_id = dag["dag_id"]

        # 스케줄 표현식 추출 (객체인 경우와 문자열인 경우 모두 처리)
        raw_interval = dag.get("schedule_interval")
        cron_expr = ""

        if isinstance(raw_interval, dict):
            cron_expr = raw_interval.get("value", "")
        else:
            cron_expr = raw_interval or ""

        if not cron_expr or not croniter.is_valid(cron_expr):
            print(f"[DEBUG] Invalid or empty cron: {cron_expr} for DAG {dag_id}")
            continue

        # 1. DAG의 시작일은 태그에서 추출
        dag_start_date = None
        tags = dag.get("tags", [])

        # 태그 형식이 문자열이나 딕셔너리 리스트일 수 있음
        for tag in tags:
            tag_value = tag
            if isinstance(tag, dict):
                tag_value = tag.get("name", "")

            # 시작일 태그 찾기 (형식: 'start_date:YYYY-MM-DD')
            if tag_value and tag_value.startswith('start_date:'):
                start_date_str = tag_value.split(':', 1)[1]
                try:
                    dag_start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    print(f"[DEBUG] Found start_date in tag for {dag_id}: {dag_start_date}")
                    break
                except ValueError:
                    pass

        # 시작일을 태그에서 찾지 못한 경우 일반 start_date 필드 사용
        if dag_start_date is None:
            start_date_str = dag.get("start_date")
            if start_date_str:
                try:
                    dag_start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                    print(f"[DEBUG] Found start_date in API field for {dag_id}: {dag_start_date}")
                except (ValueError, TypeError):
                    pass

        # 시작일이 여전히 없으면 DAG ID에서 날짜 추출 시도
        if dag_start_date is None:
            try:
                # DAG ID 형식: 'owner_name_YYYYMMDDHHMMSS'
                date_part = dag_id.split('_')[-1]

                # 날짜 부분이 숫자인지 확인
                if len(date_part) >= 8 and date_part.isdigit():
                    year_part = int(date_part[:4])
                    month_part = int(date_part[4:6])
                    day_part = int(date_part[6:8])

                    # 유효한 날짜인지 확인
                    if 2000 <= year_part <= 2100 and 1 <= month_part <= 12 and 1 <= day_part <= 31:
                        extracted_date = datetime(year_part, month_part, day_part, tzinfo=timezone.utc)
                        dag_start_date = extracted_date
                        print(f"[DEBUG] Extracted start_date from DAG ID {dag_id}: {dag_start_date}")
            except (ValueError, IndexError) as e:
                print(f"[DEBUG] Error extracting date from DAG ID {dag_id}: {str(e)}")

        # 시작일이 여전히 없으면 생성일 또는 오늘 날짜 사용
        if dag_start_date is None:
            created_date_str = dag.get("created")
            if created_date_str:
                try:
                    dag_start_date = datetime.fromisoformat(created_date_str.replace("Z", "+00:00"))
                    print(f"[DEBUG] Using created date for {dag_id}: {dag_start_date}")
                except (ValueError, TypeError):
                    # 최후의 수단으로 오늘(now) 사용
                    dag_start_date = now
                    print(f"[DEBUG] Using current date for {dag_id}: {dag_start_date}")
            else:
                # 생성일도 없으면 오늘 날짜 사용
                dag_start_date = now
                print(f"[DEBUG] Using current date for {dag_id} (no created date): {dag_start_date}")

        # 2. DAG의 종료일은 태그에서 추출
        dag_end_date = None
        for tag in tags:
            tag_value = tag
            if isinstance(tag, dict):
                tag_value = tag.get("name", "")

            # 종료일 태그 찾기 (형식: 'end_date:YYYY-MM-DD')
            if tag_value and tag_value.startswith('end_date:'):
                end_date_str = tag_value.split(':', 1)[1]
                if end_date_str != "None":
                    try:
                        dag_end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        pass

        # 종료일을 태그에서 찾지 못한 경우 일반 end_date 필드 사용
        if dag_end_date is None:
            end_date_str = dag.get("end_date")
            if end_date_str:
                try:
                    dag_end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

        # 범위 체크: 이 달의 날짜와 겹치는지 확인
        # 1. DAG 시작일이 이 달의 마지막 날보다 나중이면 스킵
        if dag_start_date > last_day:
            print(f"[DEBUG] {dag_id} start_date {dag_start_date} is after this month's last day {last_day}")
            continue

        # 2. DAG 종료일이 있고, 이 달의 첫째 날보다 이전이면 스킵
        if dag_end_date and dag_end_date < first_day:
            print(f"[DEBUG] {dag_id} end_date {dag_end_date} is before this month's first day {first_day}")
            continue

        # 유효한 시작일과 종료일 설정
        effective_start = max(dag_start_date, first_day)
        effective_end = min(dag_end_date, last_day) if dag_end_date else last_day

        if effective_start > effective_end:
            print(f"[DEBUG] {dag_id} effective_start {effective_start} > effective_end {effective_end}")
            continue

        # 실행 예정일 계산
        try:
            print(f"[DEBUG] Generating expected dates for {dag_id} from {effective_start} to {effective_end}")
            expected_dates = generate_expected_run_dates(cron_expr, effective_start, effective_end)
            print(f"[DEBUG] Expected dates for {dag_id}: {expected_dates}")
        except Exception as e:
            print(f"[Airflow] Error generating expected dates for {dag_id}: {e}")
            continue

        # 실행 이력 조회
        try:
            dag_runs = get_dag_runs(
                dag_id,
                start_date=first_day.isoformat().replace("+00:00", "Z"),
                end_date=last_day.isoformat().replace("+00:00", "Z")
            )
            executed_map = {run.get("start_date", "").split("T")[0]: run.get("state", "").lower() for run in dag_runs}
        except Exception as e:
            print(f"[Airflow] Error getting DAG runs for {dag_id}: {e}")
            executed_map = {}

        # 통계 누적 (날짜별 인덱스 사용)
        for date in expected_dates:
            if date in date_index:
                idx = date_index[date]
                all_days[idx]["total"] += 1

                state = executed_map.get(date)
                if state == "success":
                    all_days[idx]["success"] += 1
                elif state in ("failed", "error"):
                    all_days[idx]["failed"] += 1
                else:
                    all_days[idx]["pending"] += 1

    # 최종 결과 반환 (날짜별로 정렬된 상태로 유지)
    return all_days

def generate_expected_run_dates(cron_expr: str, start_date: datetime, end_date: datetime) -> List[str]:
    """
    주어진 cron 표현식과 기간 내에서 실행 예정인 날짜 리스트 반환 (YYYY-MM-DD 형식)
    """
    iter = croniter(cron_expr, start_date)
    result = []

    while True:
        next_run = iter.get_next(datetime)
        if next_run > end_date:
            break
        result.append(next_run.strftime("%Y-%m-%d"))

    return result

def get_dag_detail(dag_id: str) -> Dict[str, Any]:
    """특정 DAG의 상세 정보 조회"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}"
    
    response = requests.get(
        endpoint,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get DAG detail: {response.text}")
    
    return response.json()

def get_dag_executions_with_detail(dags: List[Dict[str, Any]], date: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    특정 날짜의 DAG 실행 상태를 상세 정보와 함께 반환 (성공, 실패, 예정 포함)
    """
    result = {
        "date": date,
        "success": [],
        "failed": [],
        "pending": []
    }

    start_date = f"{date}T00:00:00Z"
    end_date = f"{date}T23:59:59Z"

    for dag in dags:
        dag_id = dag["dag_id"]
        dag_name = dag.get("name", dag_id)
        owner = dag.get("owners", ["unknown"])[0]

        try:
            dag_runs = get_dag_runs(dag_id, start_date=start_date, end_date=end_date)

            if not dag_runs:
                # 실행 이력이 없는 경우 → 다음 실행 예정 시간을 확인해서 pending으로 분류
                next_run = dag.get("next_dagrun")
                if next_run and next_run.startswith(date):
                    result["pending"].append({
                        "schedule_id": dag_id,
                        "title": dag_name,
                        "owner": owner,
                        "next_run_time": next_run
                    })
                continue

            for run in dag_runs:
                state = run.get("state", "").lower()
                info = {
                    "schedule_id": dag_id,
                    "title": dag_name,
                    "owner": owner,
                    "last_run_time": run.get("start_date")
                }

                if state == "success":
                    result["success"].append(info)
                elif state in ("failed", "error"):
                    result["failed"].append(info)
                else:
                    result["pending"].append(info)

        except Exception as e:
            print(f"[Airflow] DAG 실행 정보 조회 실패: {dag_id} - {e}")
            continue

    return result

def delete_dag(dag_id: str) -> bool:
    """DAG 삭제"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}"
    
    response = requests.delete(
        endpoint,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    return response.status_code in (200, 204)


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
        # 1. 기존 DAG 정보 조회
        current_dag = get_dag_detail(dag_id)

        # 2. 현재 파일 경로 확인
        dag_file_path = f"/opt/airflow/dags/{dag_id}.py"
        meta_file_path = f"/opt/airflow/dags/{dag_id}.meta"

        # 3. DAG ID에서 owner 추출 (일반적으로 첫 부분)
        parts = dag_id.split('_')
        owner = parts[0]  # 기본값

        # 태그에서 owner 확인 (더 정확함)
        tags = current_dag.get("tags", [])
        for tag in tags:
            tag_value = tag
            if isinstance(tag, dict) and "name" in tag:
                tag_value = tag["name"]
            if tag_value.startswith("user_"):
                owner = tag_value
                break

        # 4. 업데이트할 값이 없으면 현재 값 유지
        current_name = current_dag.get("name", "")
        current_description = current_dag.get("description", "")
        current_schedule = current_dag.get("schedule_interval", "")

        # 변경할 값 설정
        update_name = name if name is not None else current_name
        update_description = description if description is not None else current_description
        update_schedule = cron_expression if cron_expression is not None else current_schedule

        # 5. 시작일과 종료일 설정
        # 태그에서 시작일 추출
        start_date_dt = None
        end_date_dt = None

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

        # 6. MySQL에서 job 정보 가져오기 (job_ids가 제공된 경우)
        job_details = []

        if job_ids:
            db = next(get_db())
            for job_id in job_ids:
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job:
                    raise Exception(f"Job ID {job_id}를 찾을 수 없습니다.")
                job_details.append({
                    "id": job.id,
                    "name": job.title,
                    "code": job.code
                })
        else:
            # 기존 메타 파일에서 job 목록 가져오기
            try:
                with open(meta_file_path, 'r') as f:
                    for line in f:
                        if line.startswith("JOBS:"):
                            job_ids_str = line.strip().split(':', 1)[1].strip()
                            existing_job_ids = job_ids_str.split(',')

                            # job 정보 조회
                            db = next(get_db())
                            for job_id in existing_job_ids:
                                job = db.query(Job).filter(Job.id == job_id).first()
                                if job:
                                    job_details.append({
                                        "id": job.id,
                                        "name": job.title,
                                        "code": job.code
                                    })
                            break
            except Exception as e:
                raise Exception(f"기존 job 정보 조회 실패: {str(e)}")

        # 7. 시작일과 종료일 문자열로 변환
        start_date_str = update_start_date.strftime("%Y-%m-%d")
        end_date_str = update_end_date.strftime("%Y-%m-%d") if update_end_date else "None"

        # 8. 태그 및 설명 설정
        tags_str = f"['custom', '{owner}', 'start_date:{start_date_str}'"
        if update_end_date:
            tags_str += f", 'end_date:{end_date_str}'"
        tags_str += "]"

        enhanced_description = f"{update_description} (Start: {start_date_str})"
        if update_end_date:
            enhanced_description += f", End: {end_date_str}"

        # 9. DAG 코드 생성 (동일한 DAG ID 유지)
        dag_code = f"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# START_DATE: {start_date_str}
# END_DATE: {end_date_str if update_end_date else "None"}

default_args = {{
    'owner': '{owner}',
    'depends_on_past': False,
    'start_date': datetime({update_start_date.year}, {update_start_date.month}, {update_start_date.day}),
    'end_date': {f"datetime({update_end_date.year}, {update_end_date.month}, {update_end_date.day})" if update_end_date else "None"},
    'email': [{', '.join([f"'{email}'" for email in (success_emails or [])])}],
    'email_on_failure': {bool(failure_emails or [])},
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}}

dag = DAG(
    '{dag_id}',
    default_args=default_args,
    description='{enhanced_description}',
    schedule_interval='{update_schedule}',
    tags={tags_str},
    catchup=False,
)
"""

        # 10. 각 Job에 대한 Python 함수 정의
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

        # 11. 태스크 의존성 설정 (순차 실행)
        if len(job_details) > 1:
            dag_code += "\n"
            for i in range(len(job_details) - 1):
                dag_code += f"task_{i} >> task_{i + 1}\n"

        # 12. DAG 파일 백업 및 교체
        import os

        # 백업 파일 생성 (안전장치)
        backup_file_path = f"{dag_file_path}.bak"
        try:
            import shutil
            if os.path.exists(dag_file_path):
                shutil.copy2(dag_file_path, backup_file_path)
                print(f"Created backup at {backup_file_path}")
        except Exception as e:
            print(f"Warning: Failed to create backup file: {str(e)}")

        # DAG 파일 저장 (기존 파일 교체)
        with open(dag_file_path, 'w') as f:
            f.write(dag_code)
            print(f"Updated DAG file at {dag_file_path}")

        # 13. 메타데이터 파일 업데이트
        with open(meta_file_path, 'w') as f:
            f.write(f"START_DATE: {start_date_str}\n")
            f.write(f"END_DATE: {end_date_str if update_end_date else 'None'}\n")
            f.write(f"OWNER: {owner}\n")
            f.write(f"UPDATED: {datetime.now().isoformat()}\n")
            f.write(f"JOBS: {','.join([str(job['id']) for job in job_details])}\n")
            print(f"Updated metadata file at {meta_file_path}")

        # 14. 현재 DAG 상태 유지
        try:
            # 현재 DAG 상태 유지를 위해 is_paused 값을 가져옴
            is_paused = current_dag.get("is_paused", False)

            # DAG 활성화/비활성화 상태 업데이트 (Airflow API 호출)
            toggle_dag_pause(dag_id, is_paused)
            print(f"Maintained DAG pause state: is_paused={is_paused}")
        except Exception as e:
            print(f"Warning: Failed to update DAG state via API: {str(e)}")

        # 15. 디버깅 정보 출력
        print(f"Successfully updated DAG: {dag_id}")
        print(f"- Name: {update_name}")
        print(f"- Schedule: {update_schedule}")
        print(f"- Start Date: {start_date_str}")
        print(f"- End Date: {end_date_str if update_end_date else 'None'}")
        print(f"- Jobs: {len(job_details)}")

        return True

    except Exception as e:
        # 오류 발생 시 백업에서 복원 시도
        try:
            import os
            backup_file_path = f"/opt/airflow/dags/{dag_id}.py.bak"
            dag_file_path = f"/opt/airflow/dags/{dag_id}.py"

            if os.path.exists(backup_file_path):
                import shutil
                shutil.copy2(backup_file_path, dag_file_path)
                print(f"Restored DAG file from backup after error: {str(e)}")
        except Exception as restore_error:
            print(f"Failed to restore from backup: {str(restore_error)}")

        raise Exception(f"Failed to update DAG: {str(e)}")

def get_dag_runs(
    dag_id: str, 
    limit: int = 100, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """특정 DAG의 실행 이력 조회"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"

    params = {"limit": limit}
    if start_date:
        params["start_date_gte"] = start_date
    if end_date:
        params["start_date_lte"] = end_date
    
    response = requests.get(
        endpoint,
        params=params,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get DAG runs: {response.text}")
    
    return response.json().get("dag_runs", [])

def get_dag_run_detail(dag_id: str, run_id: str) -> Dict[str, Any]:
    """특정 DAG 실행의 상세 정보 조회"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{run_id}"
    
    response = requests.get(
        endpoint,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get DAG run detail: {response.text}")
    
    return response.json()

def get_task_instances(dag_id: str, run_id: str) -> List[Dict[str, Any]]:
    """특정 DAG 실행의 태스크 인스턴스 목록 조회"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}/dagRuns/{run_id}/taskInstances"
    
    response = requests.get(
        endpoint,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get task instances: {response.text}")
    
    return response.json().get("task_instances", [])

def trigger_dag(dag_id: str) -> Dict[str, Any]:
    """특정 DAG 즉시 실행"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"
    
    request_data = {
        "conf": {}  # 필요시 설정 추가
    }
    
    response = requests.post(
        endpoint,
        json=request_data,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to trigger DAG: {response.text}")
    
    return response.json()

def toggle_dag_pause(dag_id: str, is_paused: bool) -> bool:
    """DAG 활성화/비활성화 토글"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags/{dag_id}"
    
    request_data = {
        "is_paused": is_paused
    }
    
    response = requests.patch(
        endpoint,
        json=request_data,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code not in (200, 204):
        raise Exception(f"Failed to toggle DAG pause state: {response.text}")
    
    return True


def get_dag_runs_by_date(dags: List[Dict[str, Any]], target_date: str) -> Dict[str, Any]:
    """
    특정 날짜의 DAG 실행 내역 + 실행 예정(PENDING) DAG 반환
    """
    # timezone을 일관되게 적용하기 위해 UTC 사용
    target_date_dt = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    start_dt = target_date_dt.replace(hour=0, minute=0, second=0)
    end_dt = target_date_dt.replace(hour=23, minute=59, second=59)

    start = start_dt.isoformat()
    end = end_dt.isoformat()

    result = {
        "date": target_date,
        "success": [],
        "failed": [],
        "pending": []
    }

    print(f"[DEBUG] Processing dags for date: {target_date}, dags count: {len(dags)}")

    # 대상 날짜의 문자열 형식 (YYYY-MM-DD)
    target_date_str = target_date_dt.strftime("%Y-%m-%d")

    # 모든 DAG를 순회하며 처리
    for dag in dags:
        dag_id = dag.get("dag_id")
        owner = dag.get("owners", ["unknown"])[0]
        title = dag.get("name", dag_id)
        description = dag.get("description", "")
        is_paused = dag.get("is_paused", False)

        # 비활성 DAG는 건너뛰기
        if is_paused:
            continue

        # 실행 이력 확인
        try:
            dag_runs = get_dag_runs(dag_id, start_date=start, end_date=end, limit=100)
        except Exception as e:
            print(f"[DEBUG] Error getting dag runs for {dag_id}: {e}")
            dag_runs = []

        if dag_runs:
            # 실행 기록이 있는 경우, 성공/실패에 따라 분류
            for run in dag_runs:
                state = run.get("state", "").lower()
                run_info = {
                    "schedule_id": dag_id,
                    "run_id": run.get("dag_run_id"),
                    "title": title,
                    "description": description,
                    "owner": owner,
                    "status": state,
                    "start_time": run.get("start_date"),
                    "end_time": run.get("end_date")
                }

                if state == "success":
                    result["success"].append(run_info)
                elif state in ("failed", "error"):
                    result["failed"].append(run_info)
                else:
                    result["pending"].append(run_info)
        else:
            # 실행 이력이 없는 경우, 시작일 확인 후 pending 여부 결정
            should_be_pending = False

            # 1. 시작일 추출 - DAG ID에서 날짜 부분 추출
            dag_start_date = None
            try:
                date_part = dag_id.split('_')[-1]
                if len(date_part) >= 8 and date_part.isdigit():
                    year = int(date_part[:4])
                    month = int(date_part[4:6])
                    day = int(date_part[6:8])
                    dag_start_date = datetime(year, month, day, tzinfo=timezone.utc)
                    print(f"[DEBUG] Extracted start_date from DAG ID {dag_id}: {dag_start_date}")
            except (ValueError, IndexError) as e:
                print(f"[DEBUG] Error extracting date from DAG ID {dag_id}: {str(e)}")
                dag_start_date = None

            # 2. 시작일이 대상 날짜 이전이거나 같으면 pending으로 간주
            if dag_start_date and target_date_dt >= dag_start_date:
                should_be_pending = True
                print(f"[DEBUG] {dag_id} should be pending for {target_date}")

            # 3. 시작일이 없거나 추출 실패한 경우, 기본값으로 pending 처리
            if dag_start_date is None:
                should_be_pending = True
                print(f"[DEBUG] No start_date found for {dag_id}, assuming it should be pending")

            if should_be_pending:
                # 다음 실행 시간 계산 (schedule_interval 기반)
                schedule_interval = dag.get("schedule_interval", "")
                next_run_time = None

                if isinstance(schedule_interval, dict) and "value" in schedule_interval:
                    schedule_interval = schedule_interval["value"]

                if schedule_interval and croniter.is_valid(schedule_interval):
                    try:
                        # 크론 표현식에서 다음 실행 시간 계산
                        cron_iter = croniter(schedule_interval, start_dt)
                        next_run_time = cron_iter.get_next(datetime).isoformat()
                    except Exception as e:
                        print(f"[DEBUG] Error calculating next run time for {dag_id}: {str(e)}")

                result["pending"].append({
                    "schedule_id": dag_id,
                    "title": title,
                    "description": description,
                    "owner": owner,
                    "status": "pending",
                    "next_run_time": next_run_time
                })

    # 결과 출력
    print(
        f"[DEBUG] Final result for {target_date}: success={len(result['success'])}, failed={len(result['failed'])}, pending={len(result['pending'])}")

    return result

def get_schedule_detail(schedule_id: str) -> Dict[str, Any]:
    """
    스케줄(DAG) 상세 정보 조회와 관련 job 정보를 함께 반환
    """
    db = next(get_db())

    try:
        # DAG 상세 정보 조회
        dag_detail = get_dag_detail(schedule_id)

        # 메타데이터에서 추가 정보 조회
        metadata = get_dag_metadata(schedule_id)

        # job 정보 조회 (데이터베이스에서)
        tasks = []
        job_ids = metadata.get("job_ids", [])
        for idx, job_id in enumerate(job_ids):
            # DB에서 job 정보 조회
            job_info = crud.get_job_by_id(db, job_id)

            task = {
                "id": job_id,
                "order": idx + 1
            }

            # job_info가 있으면 title과 description 추가
            if job_info:
                task["title"] = job_info.get("title", "")
                task["description"] = job_info.get("description", "")

            tasks.append(task)

        # 크론 표현식 처리
        frequency_cron = ""
        if "schedule_interval" in dag_detail:
            schedule_interval = dag_detail.get("schedule_interval")
            if isinstance(schedule_interval, dict) and "__type" in schedule_interval:
                frequency_cron = schedule_interval.get("value", "")
            else:
                frequency_cron = schedule_interval

        # 주기 문자열로 변환 (역변환)
        frequency = convert_cron_to_frequency(frequency_cron)
        frequency_display = parse_cron_to_friendly_format(frequency_cron)
        # execution_time이 메타데이터에 없으면 cron에서 추출
        execution_time = metadata.get("execution_time")
        if not execution_time:
            execution_time = extract_execution_time_from_cron(dag_detail.get("schedule_interval"))

        # 응답 데이터 구성
        schedule_data = {
            "schedule_id": schedule_id,
            "title": dag_detail.get("name", schedule_id),
            "description": dag_detail.get("description", ""),
            "frequency": frequency,
            "frequency_cron": frequency_cron,
            "frequency_display": frequency_display,
            "is_paused": dag_detail.get("is_paused", False),
            "created_at": dag_detail.get("created_at", datetime.now().isoformat()),
            "updated_at": dag_detail.get("updated_at", None),
            "start_date": metadata.get("start_date"),
            "end_date": metadata.get("end_date"),
            "execution_time": execution_time,
            "success_emails": metadata.get("success_emails", []),
            "failure_emails": metadata.get("failure_emails", []),
            "jobs": tasks
        }

        return schedule_data

    finally:
        db.close()

def extract_execution_time_from_cron(cron_expression: str) -> Optional[str]:
    """
    cron 표현식에서 실행 시간(HH:MM) 추출
    """
    if not cron_expression:
        return None

    if isinstance(cron_expression, dict) and "__type" in cron_expression and cron_expression[
        "__type"] == "CronExpression":
        cron_parts = cron_expression.get("value", "").split(" ")
    else:
        cron_parts = cron_expression.strip().split(" ")

    if len(cron_parts) >= 2:
        minute, hour = cron_parts[0], cron_parts[1]
        # 간단한 시간 형식인 경우만 처리 (*/2 같은 복잡한 패턴은 제외)
        if hour.isdigit() and minute.isdigit():
            return f"{int(hour):02d}:{int(minute):02d}"

    return None


def convert_cron_to_frequency(cron_expression: str) -> str:
    """
    cron 표현식을 사용자 친화적인 주기 표현으로 변환
    """
    if not cron_expression:
        return ""

    parts = cron_expression.strip().split(" ")
    if len(parts) < 5:
        return cron_expression  # 유효하지 않은 cron 표현식은 그대로 반환

    minute, hour, day_of_month, month, day_of_week = parts[:5]

    # 일일 주기 (특정 시간에 매일)
    if day_of_month == "*" and month == "*" and day_of_week == "*":
        return "daily"

    # 주간 주기 (특정 요일마다)
    if day_of_month == "*" and month == "*" and day_of_week.isdigit():
        return "weekly"

    # 월간 주기 (매월 특정 일)
    if day_of_month.isdigit() and month == "*" and day_of_week == "*":
        return "monthly"

    # 시간 간격 주기
    if hour.startswith("*/") and day_of_month == "*" and month == "*" and day_of_week == "*":
        interval = hour.replace("*/", "")
        if interval.isdigit():
            return f"every_{interval}_hours"

    # 일 간격 주기
    if day_of_month.startswith("*/") and month == "*" and day_of_week == "*":
        interval = day_of_month.replace("*/", "")
        if interval.isdigit():
            # 7의 배수면 주 단위로 변환
            if int(interval) % 7 == 0 and int(interval) > 0:
                weeks = int(interval) // 7
                return f"every_{weeks}_weeks"
            return f"every_{interval}_days"

    # 변환할 수 없는 경우 원본 표현식 반환
    return cron_expression


def get_dag_metadata(dag_id: str) -> Dict[str, Any]:
    """
    메타데이터 파일에서 DAG 추가 정보 조회
    """
    metadata = {
        "job_ids": [],
        "start_date": None,
        "end_date": None,
        "success_emails": [],
        "failure_emails": [],
        "execution_time": None
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
        except Exception as e:
            print(f"Error reading metadata file: {str(e)}")

    return metadata


def parse_cron_to_friendly_format(cron_expression: str) -> dict:
    """
    cron 표현식을 사용자 친화적인 형식으로 변환

    예시:
    "0 9 * * *" -> {"type": "daily", "time": "09:00"}
    "0 9 * * 1" -> {"type": "weekly", "dayOfWeek": "Mon", "time": "09:00"}
    "0 0 1 * *" -> {"type": "monthly", "dayOfMonth": 1, "time": "00:00"}
    """
    if not cron_expression:
        return None

    # cron 형식이 아닌 경우 처리
    if not isinstance(cron_expression, str) or cron_expression.count(" ") < 4:
        return None

    parts = cron_expression.strip().split()
    if len(parts) < 5:
        return None

    minute, hour, day_of_month, month, day_of_week = parts[:5]

    # 시간 형식 변환
    time_str = f"{int(hour):02d}:{int(minute):02d}" if hour.isdigit() and minute.isdigit() else "00:00"

    # 일간 (모든 날짜, 모든 월, 모든 요일)
    if day_of_month == "*" and month == "*" and day_of_week == "*":
        return {"type": "daily", "time": time_str}

    # 주간 (모든 날짜, 모든 월, 특정 요일)
    if day_of_month == "*" and month == "*" and day_of_week != "*":
        # 요일 변환 (0,7=일요일, 1=월요일, ..., 6=토요일)
        day_of_week_num = int(day_of_week) if day_of_week.isdigit() else 1
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        day_name = days[day_of_week_num % 7] if day_of_week_num != 7 else days[0]
        return {"type": "weekly", "dayOfWeek": day_name, "time": time_str}

    # 월간 (특정 날짜, 모든 월, 모든 요일)
    if day_of_month != "*" and month == "*" and (day_of_week == "*" or day_of_week == "?"):
        day = int(day_of_month) if day_of_month.isdigit() else 1
        return {"type": "monthly", "dayOfMonth": day, "time": time_str}

    # 기타 복잡한 경우 원본 cron 표현식 반환
    return {"type": "custom", "cronExpression": cron_expression}

def get_all_schedules_with_details(
        status: Optional[str] = None,
        search: Optional[str] = None,
        include_job_status: bool = False
) -> List[Dict[str, Any]]:
    """
    모든 스케줄(DAG) 목록을 상세 정보와 함께 반환

    Args:
        status: 필터링할 상태 (active/paused)
        search: 검색어 (제목, 설명에서 검색)
        include_job_status: 작업 상태 포함 여부

    Returns:
        스케줄 목록 (각 스케줄의 상세 정보 포함)
    """
    # 모든 DAG 기본 정보 조회
    dags = get_all_dags(limit=1000)

    # 상태별 필터링
    if status:
        if status.lower() == "active":
            dags = [dag for dag in dags if not dag.get("is_paused", False)]
        elif status.lower() == "paused":
            dags = [dag for dag in dags if dag.get("is_paused", False)]

    # 제목 검색
    if search:
        search = search.lower()
        dags = [dag for dag in dags if search in dag.get("dag_id", "").lower() or
                search in dag.get("description", "").lower()]

    # 각 DAG의 상세 정보 조회
    schedule_list = []
    db = next(get_db())
    try:
        for dag in dags:
            dag_id = dag.get("dag_id", "")

            try:
                # 상세 정보 조회
                schedule_data = get_schedule_detail(dag_id)

                # 작업 상태 포함 여부에 따라 최근 실행 정보 조회
                if include_job_status:
                    # 최근 실행 정보 조회
                    recent_runs = get_dag_runs(dag_id, limit=1)

                    if recent_runs:
                        recent_run = recent_runs[0]
                        run_id = recent_run.get("dag_run_id")

                        # 작업 실행 상태 조회
                        task_instances = get_task_instances(dag_id, run_id)

                        # 작업 정보에 상태 추가
                        tasks_with_status = []
                        for job in schedule_data.get("jobs", []):
                            job_id = job.get("id")
                            # 해당 job_id와 일치하는 태스크 인스턴스 찾기
                            matching_task = None
                            for task in task_instances:
                                task_id = task.get("task_id", "")
                                if task_id == f"job_{job_id}":
                                    matching_task = task
                                    break

                            # 작업 정보에 상태 추가
                            job_with_status = job.copy()
                            if matching_task:
                                job_with_status["status"] = matching_task.get("state", "unknown")
                                job_with_status["start_time"] = matching_task.get("start_date")
                                job_with_status["end_time"] = matching_task.get("end_date")
                                job_with_status["duration"] = matching_task.get("duration")
                            else:
                                job_with_status["status"] = "not_run"

                            tasks_with_status.append(job_with_status)

                        # 원래 jobs 배열 교체
                        schedule_data["jobs"] = tasks_with_status

                        # 실행 정보 추가
                        schedule_data["last_run"] = {
                            "run_id": run_id,
                            "status": recent_run.get("state"),
                            "start_time": recent_run.get("start_date"),
                            "end_time": recent_run.get("end_date")
                        }

                schedule_list.append(schedule_data)
            except Exception as detail_err:
                print(f"Error getting detail for {dag_id}: {str(detail_err)}")
                # 오류 시 기본 정보만 추가
                schedule_list.append({
                    "schedule_id": dag_id,
                    "title": dag.get("description", "").split(" (Start:")[0] or dag_id,
                    "description": dag.get("description", ""),
                    "is_paused": dag.get("is_paused", False),
                    "frequency": "unknown",
                    "jobs": []
                })
    finally:
        db.close()

    return schedule_list