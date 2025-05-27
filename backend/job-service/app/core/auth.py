import os
from http import HTTPStatus

import requests
from app.core.constants import USER_NAME, USER_DEPARTMENT, USER_ROLE
from dotenv import load_dotenv
from fastapi import Request, HTTPException

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL") # User-Service End-Point

# Middleware를 통해 넘어온 header에서 x-user-id를 추출합니다.
def get_user_id_from_header(request: Request) -> int:
    user_id = request.headers.get("x-user-id")
    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid x-user-id header")

# x-user-id를 이용해 User-Service로 요청을 보내 사용자 상세 정보를 조회합니다.
def get_user_info(user_id: int):
    url = USER_SERVICE_URL
    headers = {
        "x-user-id": str(user_id)
    }

    response = requests.get(url, headers=headers)

    # User-Service 호출이 정상적으로 이루어졌다면, 사용자 정보를 추출합니다.
    if response.status_code == HTTPStatus.OK:
        user_data = response.json()
        name = user_data.get("data").get(USER_NAME)
        department = user_data.get("data").get(USER_DEPARTMENT)
        role = user_data.get("data").get(USER_ROLE)

        return {
            USER_NAME: name,
            USER_DEPARTMENT: department,
            USER_ROLE: role
        }
    else:
        return None