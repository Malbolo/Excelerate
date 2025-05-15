import os
from http import HTTPStatus

import requests
from app.core.constants import USER_NAME, USER_DEPARTMENT, USER_ROLE
from dotenv import load_dotenv
from fastapi import Request, HTTPException

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

def get_user_id_from_header(request: Request) -> int:
    user_id = request.headers.get("x-user-id")
    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid x-user-id header")

def get_user_info(user_id: int):
    url = USER_SERVICE_URL
    headers = {
        "x-user-id": str(user_id)
    }

    response = requests.get(url, headers=headers)

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