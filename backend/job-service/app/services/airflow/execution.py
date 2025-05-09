import requests
from typing import Dict, Any

from app.core.config import settings


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