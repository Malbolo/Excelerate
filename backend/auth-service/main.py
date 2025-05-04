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
    user_role = ""

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

            if "exp" in payload and payload["exp"] < time.time():
                return JSONResponse(status_code=401, content={"detail": "Token expired"})

            user_id = str(payload.get("sub", ""))
            user_role = str(payload.get("role", ""))

        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    response: Response = await call_next(request)
    response.headers["X-User-Id"] = user_id
    response.headers["X-User-Role"] = user_role
    return response

@app.get("/api/auth/ping")
def ping():
    return {"message": "auth-service is up"}
