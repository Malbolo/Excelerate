import os
from fastapi import Request, HTTPException
import requests
from dotenv import load_dotenv

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

def get_user_id_from_header(request: Request) -> int:
    if DEV_MODE:
        return 1
    user_id = request.headers.get("x-user-id")

    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid x-user-id header")

def get_user_info(user_id: int):
    if DEV_MODE:
        return {
            "name": "DevAdmin",
            "department": "Development",
            "role": "ADMIN"
        }

    url = USER_SERVICE_URL
    headers = {
        "x-user-id": str(user_id)
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        name = user_data.get("data").get("name")
        department = user_data.get("data").get("department")
        role = user_data.get("data").get("role")

        return {
            "name": name,
            "department": department,
            "role": role
        }
    else:
        return None

def call_service_api(service_url, method="GET", endpoint="", data=None, user_id=None):
    """
    다른 마이크로서비스의 API를 호출하는 헬퍼 함수

    Args:
        service_url: 마이크로서비스 기본 URL (환경변수에서 가져옴)
        method: HTTP 메서드 (GET, POST, PUT, DELETE 등)
        endpoint: API 엔드포인트 경로
        data: 요청 본문 데이터 (dict)
        user_id: 사용자 ID (인증 헤더에 포함)

    Returns:
        API 응답 (JSON)
    """
    if not service_url:
        raise Exception(f"서비스 URL이 설정되지 않았습니다.")

    # URL 조합
    url = f"{service_url}{endpoint}"

    # 인증 헤더 설정
    headers = {
        "Content-Type": "application/json",
        "x-user-id": str(user_id)
    }
    # None 값 제거
    headers = {k: v for k, v in headers.items() if v is not None}

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, json=data)
        else:
            raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

        # 응답 상태 코드 확인
        if response.status_code >= 400:
            raise Exception(f"API 호출 실패: {response.status_code} - {response.text}")

        return response.json()

    except requests.RequestException as e:
        raise Exception(f"서비스 API 호출 중 오류 발생: {str(e)}")