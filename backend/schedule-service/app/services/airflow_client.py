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

    def get_all_dags(
            self,
            limit: int = 200,
            offset: int = 0,  # 오프셋 파라미터 추가
            fields: List[str] = None,
            order_by: str = None,
            paused: Optional[bool] = None,
            only_active: bool = True
    ) -> dict[str, Any]:
        """모든 DAG 목록 조회 (옵션: 필드 제한, 정렬, 필터링, 페이지네이션)"""
        params = {"limit": limit, "offset": offset}  # offset 파라미터 추가

        if fields:
            params["fields"] = fields
        if order_by:
            params["order_by"] = order_by
        if paused is not None:  # paused 값이 명시적으로 제공된 경우만 포함
            params["paused"] = paused
        if not only_active:  # only_active의 기본값은 True
            params["only_active"] = only_active

        return self._get("dags", params)

    def get_dag_detail(self, dag_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """특정 DAG의 상세 정보 조회"""
        params = {}
        if fields:
            params["fields"] = fields

        return self._get(f"dags/{dag_id}", params)

    def get_dag_runs(
            self,
            dag_id: str,
            limit: int = 100,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """특정 DAG의 실행 이력 조회"""
        params = {"limit": limit}
        if start_date:
            params["start_date_gte"] = start_date
        if end_date:
            params["start_date_lte"] = end_date
        if fields:
            params["fields"] = fields

        response = self._get(f"dags/{dag_id}/dagRuns", params)
        return response.get("dag_runs", [])

    def get_dag_run_detail(self, dag_id: str, run_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """특정 DAG 실행의 상세 정보 조회"""
        params = {}
        if fields:
            params["fields"] = fields

        return self._get(f"dags/{dag_id}/dagRuns/{run_id}", params)

    def get_task_instances(self, dag_id: str, run_id: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        """특정 DAG 실행의 태스크 인스턴스 목록 조회"""
        params = {}
        if fields:
            params["fields"] = fields

        response = self._get(f"dags/{dag_id}/dagRuns/{run_id}/taskInstances", params)
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
                    # JSON 응답의 content 필드에서 로그 내용 추출, 인코딩 처리
                    content = response.json().get("content", "")
                    # JSON으로 파싱된 경우 인코딩 이슈가 적을 수 있으나, 확인 필요
                    return content

                # 일반 텍스트 응답일 경우 UTF-8로 명시적 디코딩
                response.encoding = 'utf-8'  # 명시적으로 인코딩 설정
                return response.text  # requests는 자동으로 인코딩을 감지하여 text로 변환

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

# 클라이언트 인스턴스 생성
airflow_client = AirflowClient()