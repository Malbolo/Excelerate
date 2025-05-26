# auth-service 인수인계서

# 디렉터리 구조

auth-service/
└── [main.py](http://main.py) 

---

# main.py

JWT 토큰을 검증하여 사용자 인증 정보를 확인하고 header에 포함하여 전달하는 Middleware 역할을 수행합니다.

각 환경 변수는 env 파일에 분리되어 있습니다.

- JWT 인증
    - 클라이언트가 Authorization Header 에 JWT 토큰을 `Beader {token}` 형식으로 전달하면 이를 파싱 및 디코딩하여 유효성 검사를 수행합니다.
    - 토큰 만료 여부를 검사합니다.
- 사용자 정보 추출 및 전달
    - JWT 토큰에서 값을 추출해 x-user-id, x-user-role 을 header에 삽입합니다.
- 프론트엔드 개발 편의성을 위해 [`http://localhost:5173`](http://localhost:5173) 의 CORS 설정이 되어있습니다.