from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import jwt
import time
import os
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-User-Id", "X-User-Role"]
)

encoded_key = os.getenv("JWT_SECRET")
JWT_SECRET = base64.b64decode(encoded_key)

@app.get("/auth")
def forward_auth(Authorization: str = Header(None)):
    user_id = ""
    user_role = ""

    if Authorization and Authorization.startswith("Bearer "):
        token = Authorization[7:]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if "exp" in payload and payload["exp"] < time.time():
                return JSONResponse(
                    status_code=401,
                    content={
                        "result": "error",
                        "code": "002",
                        "message": "Token expired"
                    }
                )
            user_id = str(payload.get("sub", ""))
            user_role = str(payload.get("role", ""))
        except jwt.InvalidTokenError:
            pass

    response = JSONResponse(content={"status": "ok"})
    response.headers["X-User-Id"] = user_id
    response.headers["X-User-Role"] = user_role
    return response
