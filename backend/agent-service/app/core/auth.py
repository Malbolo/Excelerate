from fastapi import Request, HTTPException
import requests

def get_user_id_from_header(request: Request) -> str | None:
    user_id = request.headers.get("x-user-id")
    try:
        if not user_id:
            return None
        return user_id
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid x-user-id header")

def get_user_info(user_id: str):
    url = "http://user-service.user-service.svc.cluster.local:8080/api/users/me/profile"
    headers = {
        "x-user-id": user_id
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
    
class CurrentUser:
    def __init__(self, user_id: str, user_name: str):
        self.id = user_id
        self.name = user_name


def get_current_user(request: Request) -> CurrentUser:
    """
    FastAPI Dependency: 요청 헤더에서 사용자 정보를 추출하여 CurrentUser 객체로 반환합니다.
    헤더에 x-user-id가 없거나, 조회가 실패하면 user_id와 user_name을 "guest"로 설정합니다.
    """
    try:
        user_id = get_user_id_from_header(request) or "guest"
        profile = get_user_info(user_id)
        if profile and isinstance(profile, dict):
            user_name = profile.get("name") or "guest"
        else:
            user_name = "guest"
    except:
        user_id = "guest"
        user_name = "guest"
    return CurrentUser(user_id, user_name)