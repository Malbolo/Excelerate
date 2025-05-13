import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import calendar

from app.core.config import settings
from app.services.utils.time import get_month_date_range, format_date_for_airflow


def get_dags_by_owner(owner: str) -> List[Dict[str, Any]]:
    """특정 소유자(owner)의 DAG 목록 조회"""
    endpoint = f"{settings.AIRFLOW_API_URL}/dags"
    params = {
        "tags": owner,
        "limit": 100
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


def get_task_logs(schedule_id: str, run_id: str, task_id: str, try_number: Optional[int] = None) -> str:
    """Airflow API에서 태스크 로그를 가져옵니다."""
    try:
        # 시도 번호가 명시되지 않은 경우, 태스크 인스턴스 정보를 조회하여 최신 시도 번호 얻기
        if try_number is None:
            # 태스크 인스턴스 정보 조회
            task_info_endpoint = f"{settings.AIRFLOW_API_URL}/dags/{schedule_id}/dagRuns/{run_id}/taskInstances/{task_id}"

            task_info_response = requests.get(
                task_info_endpoint,
                auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
            )

            if task_info_response.status_code == 200:
                task_info = task_info_response.json()
                try_number = task_info.get("try_number", 1)
            else:
                print(f"Failed to get task instance info. Status code: {task_info_response.status_code}")
                try_number = 1  # 기본값으로 1 사용

        # 로그 조회 엔드포인트 구성
        logs_endpoint = f"{settings.AIRFLOW_API_URL}/dags/{schedule_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs/{try_number}"

        # API 요청 (텍스트 형식으로 요청)
        headers = {"Accept": "text/plain"}
        response = requests.get(
            logs_endpoint,
            headers=headers,
            auth=(settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
        )

        if response.status_code == 200:
            # 응답이 JSON인지 확인
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                log_data = response.json()
                return log_data.get("content", "")
            else:
                # 텍스트 응답
                return response.text
        else:
            print(f"Failed to get task logs. Status code: {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error getting task logs: {str(e)}")
        return ""


def get_next_dag_run(dag_id: str) -> Optional[Dict[str, Any]]:
    """특정 DAG의 다음 실행 예정 정보를 조회"""
    try:
        # DAG 상세 정보 조회
        dag_detail = get_dag_detail(dag_id)

        # DAG가 비활성화된 경우 다음 실행이 없음
        if dag_detail.get("is_paused", True):
            return None

        # 다음 실행 날짜 확인
        next_dagrun = dag_detail.get("next_dagrun")

        if next_dagrun:
            return {
                "execution_date": next_dagrun,
                "scheduled_time": dag_detail.get("next_dagrun_data_interval_start", next_dagrun),
                "data_interval_end": dag_detail.get("next_dagrun_data_interval_end")
            }

        return None
    except Exception as e:
        print(f"Error getting next DAG run for {dag_id}: {str(e)}")
        return None