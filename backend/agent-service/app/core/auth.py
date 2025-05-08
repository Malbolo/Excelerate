from fastapi import Request, HTTPException
import requests

def get_user_id_from_header(request: Request) -> int:
    user_id = request.headers.get("x-user-id")
    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid x-user-id header")

def get_user_info(user_id: int):
    url = "http://user-service.user-service.svc.cluster.local:8080/api/users/me/profile"
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