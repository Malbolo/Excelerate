import requests
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.log_config import logger


class AirflowClient:
    """Airflow API와 통신하는 클라이언트 클래스"""
    def __init__(self):
        self.base_url = settings.AIRFLOW_API_URL
        self.auth = (settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)
        logger.info(f"AirflowClient initialized with base URL: {self.base_url}")

    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """GET 요청 수행"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Sending GET request to {url} with params: {params}")
            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Airflow API GET 요청 오류: {str(e)}")
            raise Exception(f"Airflow API 호출 실패: {str(e)}")

    def _post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """POST 요청 수행"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Sending POST request to {url} with data: {data}")
            response = requests.post(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Airflow API POST 요청 오류: {str(e)}")
            raise Exception(f"Airflow API 호출 실패: {str(e)}")

    def _patch(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """PATCH 요청 수행"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Sending PATCH request to {url} with data: {data}")
            response = requests.patch(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Airflow API PATCH 요청 오류: {str(e)}")
            raise Exception(f"Airflow API 호출 실패: {str(e)}")

    def _delete(self, endpoint: str) -> bool:
        """DELETE 요청 수행"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Sending DELETE request to {url}")
            response = requests.delete(url, auth=self.auth)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Airflow API DELETE 요청 오류: {str(e)}")
            raise Exception(f"Airflow API 호출 실패: {str(e)}")

    # DAG 관련 메서드

    def get_all_dags(self, limit: int = 200, fields: List[str] = None, order_by: str = None) -> List[Dict[str, Any]]:
        """모든 DAG 목록 조회 (옵션: 필드 제한, 정렬)"""
        params = {"limit": limit}
        if fields:
            params["fields"] = fields
        if order_by:
            params["order_by"] = order_by

        response = self._get("dags", params)
        return response.get("dags", [])

    def get_dags_by_owner(self, owner: str, limit: int = 100) -> List[Dict[str, Any]]:
        """특정 소유자(owner)의 DAG 목록 조회"""
        response = self._get("dags", {"tags": owner, "limit": limit})
        return response.get("dags", [])

    def get_dag_detail(self, dag_id: str) -> Dict[str, Any]:
        """특정 DAG의 상세 정보 조회"""
        return self._get(f"dags/{dag_id}")

    def get_dag_runs(
            self,
            dag_id: str,
            limit: int = 100,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """특정 DAG의 실행 이력 조회"""
        params = {"limit": limit}
        if start_date:
            params["start_date_gte"] = start_date
        if end_date:
            params["start_date_lte"] = end_date

        response = self._get(f"dags/{dag_id}/dagRuns", params)
        return response.get("dag_runs", [])

    def get_dag_run_detail(self, dag_id: str, run_id: str) -> Dict[str, Any]:
        """특정 DAG 실행의 상세 정보 조회"""
        return self._get(f"dags/{dag_id}/dagRuns/{run_id}")

    def get_task_instances(self, dag_id: str, run_id: str) -> List[Dict[str, Any]]:
        """특정 DAG 실행의 태스크 인스턴스 목록 조회"""
        response = self._get(f"dags/{dag_id}/dagRuns/{run_id}/taskInstances")
        return response.get("task_instances", [])

    def get_task_logs(self, schedule_id: str, run_id: str, task_id: str, try_number: Optional[int] = None) -> str:
        """태스크 로그 조회"""
        # 시도 번호가 없으면 태스크 인스턴스에서 가져오기
        if try_number is None:
            try:
                task_info = self._get(f"dags/{schedule_id}/dagRuns/{run_id}/taskInstances/{task_id}")
                try_number = task_info.get("try_number", 1)
            except Exception as e:
                logger.warning(f"태스크 정보 조회 실패, 기본값 사용: {str(e)}")
                try_number = 1

        # 로그 조회
        url = f"{self.base_url}/dags/{schedule_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs/{try_number}"
        headers = {"Accept": "text/plain"}

        try:
            logger.debug(f"Requesting task logs from {url}")
            response = requests.get(url, headers=headers, auth=self.auth)
            if response.status_code == 200:
                # 응답이 JSON인지 확인
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return response.json().get("content", "")
                return response.text
            logger.warning(f"로그 조회 실패: {response.status_code}")
            return ""
        except Exception as e:
            logger.error(f"로그 조회 중 오류 발생: {str(e)}")
            return ""

    def trigger_dag(self, dag_id: str) -> Dict[str, Any]:
        """DAG 실행 트리거"""
        return self._post(f"dags/{dag_id}/dagRuns", {"conf": {}})

    def toggle_dag_pause(self, dag_id: str, is_paused: bool) -> bool:
        """DAG 활성화/비활성화 토글"""
        self._patch(f"dags/{dag_id}", {"is_paused": is_paused})
        return True

    def delete_dag(self, dag_id: str) -> bool:
        """DAG 삭제"""
        return self._delete(f"dags/{dag_id}")

    def get_next_dag_run(self, dag_id: str) -> Optional[Dict[str, Any]]:
        """특정 DAG의 다음 실행 예정 정보를 조회"""
        try:
            # DAG 상세 정보 조회
            dag_detail = self.get_dag_detail(dag_id)

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
            logger.error(f"다음 DAG 실행 정보 조회 중 오류 발생: {str(e)}")
            return None

# 클라이언트 인스턴스 생성
airflow_client = AirflowClient()