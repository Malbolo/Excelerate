import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import calendar
import os
from croniter import croniter

class Settings:
    AIRFLOW_API_BASE_URL: str = os.getenv("AIRFLOW_API_BASE_URL", "http://job-service-airflow-webserver-1:8080/api/v1")
    AIRFLOW_USERNAME: str = os.getenv("AIRFLOW_USERNAME", "airflow")
    AIRFLOW_PASSWORD: str = os.getenv("AIRFLOW_PASSWORD", "airflow")

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
        failure_emails: List[str] = None
) -> str:
    # DAG ID는 고유해야 함
    dag_id = f"{owner}_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 시작일과 종료일 문자열로 변환 (태그에 저장하기 위함)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "None"

    # 태그 리스트 생성 (문자열로 변환하여 저장)
    # 문자열 형식으로 명확하게 지정
    tags_str = f"['custom', '{owner}', 'start_date:{start_date_str}'"
    if end_date:
        tags_str += f", 'end_date:{end_date_str}'"
    tags_str += "]"

    # 또한 설명에도 시작일 정보를 포함
    enhanced_description = f"{description} (Start: {start_date_str})"
    if end_date:
        enhanced_description += f", End: {end_date_str}"

    # DAG 코드 생성 (기존 코드 재사용)
    dag_code = f"""
from airflow import DAG
from airflow.operators.bash import BashOperator
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
)
"""

    # Job을 DAG 태스크로 변환
    for idx, job_id in enumerate(job_ids):
        task_id = f"job_{job_id}"
        dag_code += f"""
task_{idx} = BashOperator(
    task_id='{task_id}',
    bash_command='python /app/execute_job.py --job-id {job_id}',
    dag=dag,
)
"""

    # 태스크 의존성 설정 (순차 실행)
    if len(job_ids) > 1:
        dag_code += "\n"
        for i in range(len(job_ids) - 1):
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

        # 또한 메타데이터 파일도 생성 (백업 방법)
        meta_file_path = f"/opt/airflow/dags/{dag_id}.meta"
        with open(meta_file_path, 'w') as f:
            f.write(f"START_DATE: {start_date_str}\n")
            f.write(f"END_DATE: {end_date_str if end_date else 'None'}\n")
            f.write(f"OWNER: {owner}\n")
            f.write(f"CREATED: {datetime.now().isoformat()}\n")

        return dag_id
    except Exception as e:
        raise Exception(f"Failed to create DAG file: {str(e)}")

def get_dags_by_owner(owner: str) -> List[Dict[str, Any]]:
    """특정 소유자(owner)의 DAG 목록 조회"""
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags"
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
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags"
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
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}"
    
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
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}"
    
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
    """기존 DAG 업데이트"""
    # 현재 DAG 정보 조회
    current_dag = get_dag_detail(dag_id)
    
    # 업데이트할 값이 없으면 현재 값 유지
    owner = current_dag.get("owner", "airflow")
    dag_description = description or current_dag.get("description", "")
    schedule_interval = cron_expression or current_dag.get("schedule_interval", "0 0 * * *")
    
    # DAG 파일 코드 생성
    # (실제로는 Airflow API를 통해 DAG 코드를 업데이트하는 방식이 더 복잡할 수 있음)
    
    # Airflow API 요청 데이터
    request_data = {
        "is_paused": False,
        "schedule_interval": schedule_interval,
        "description": dag_description
    }
    
    # API 호출
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}"
    response = requests.patch(
        endpoint,
        json=request_data,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code not in (200, 204):
        raise Exception(f"Failed to update DAG: {response.text}")
    
    return True

def get_dag_runs(
    dag_id: str, 
    limit: int = 100, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """특정 DAG의 실행 이력 조회"""
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}/dagRuns"

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
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}/dagRuns/{run_id}"
    
    response = requests.get(
        endpoint,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get DAG run detail: {response.text}")
    
    return response.json()

def get_task_instances(dag_id: str, run_id: str) -> List[Dict[str, Any]]:
    """특정 DAG 실행의 태스크 인스턴스 목록 조회"""
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}/dagRuns/{run_id}/taskInstances"
    
    response = requests.get(
        endpoint,
        auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get task instances: {response.text}")
    
    return response.json().get("task_instances", [])

def trigger_dag(dag_id: str) -> Dict[str, Any]:
    """특정 DAG 즉시 실행"""
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}/dagRuns"
    
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
    endpoint = f"{settings.AIRFLOW_API_BASE_URL}/dags/{dag_id}"
    
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
                    "dag_id": dag_id,
                    "title": title,
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
                result["pending"].append({
                    "dag_id": dag_id,
                    "title": title,
                    "owner": owner,
                    "status": "pending",
                    "start_time": None,
                    "end_time": None
                })

    # 결과 출력
    print(
        f"[DEBUG] Final result for {target_date}: success={len(result['success'])}, failed={len(result['failed'])}, pending={len(result['pending'])}")

    return result