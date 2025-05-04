from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
import jwt
import time
import os

app = FastAPI()
JWT_SECRET = os.getenv("JWT_SECRET")

@app.get("/auth")
def forward_auth(Authorization: str = Header(None)):
    user_id = ""
    user_role = ""

    if Authorization and Authorization.startswith("Bearer "):
        token = Authorization[7:]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if "exp" in payload and payload["exp"] < time.time():
                return JSONResponse(status_code=401, content={"detail": "Token expired"})

            user_id = str(payload.get("sub", ""))
            user_role = str(payload.get("role", ""))
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    response = JSONResponse(content={"status": "ok"})
    response.headers["X-User-Id"] = user_id
    response.headers["X-User-Role"] = user_role
    return response
