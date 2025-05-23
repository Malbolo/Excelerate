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
    allow_origins=["http://localhost:5173"], # 프론트 로컬 테스트를 위한 origin 허용
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

    # Authorization 헤더에 Bearer로 시작하는 토큰 사용 중.
    if Authorization and Authorization.startswith("Bearer "):
        token = Authorization[7:] # Bearer 제거
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

            # 토큰 만료 시 Unauthorized
            if "exp" in payload and payload["exp"] < time.time():
                return JSONResponse(
                    status_code=401,
                    content={
                        "result": "error",
                        "code": "002",
                        "message": "Token expired"
                    }
                )

            # 사용자 정보 추출
            user_id = str(payload.get("sub", ""))
            user_role = str(payload.get("role", ""))
        except jwt.InvalidTokenError:
            pass

    response = JSONResponse(content={"status": "ok"})

    # 응답 헤더에 사용자 정보 담아 전달
    response.headers["X-User-Id"] = user_id
    response.headers["X-User-Role"] = user_role
    return response
