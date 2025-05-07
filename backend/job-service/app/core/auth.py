from fastapi import Request, HTTPException

def get_user_id_from_header(request: Request) -> int:
    user_id = request.headers.get("x-user-id")
    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid x-user-id header")