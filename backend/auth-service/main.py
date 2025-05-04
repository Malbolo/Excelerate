from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import os
import jwt
import time

app = FastAPI()

JWT_SECRET = os.getenv("JWT_SECRET")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    user_id = ""

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # exp 검증
            if "exp" in payload and payload["exp"] < time.time():
                return JSONResponse(status_code=401, content={"detail": "Token expired"})

            user_id = str(payload.get("sub", ""))
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    # x-user-id 헤더 삽입
    response: Response = await call_next(request)
    response.headers["x-user-id"] = user_id
    return response

@app.get("/api/auth/ping")
def ping():
    return {"message": "auth-service is up"}
