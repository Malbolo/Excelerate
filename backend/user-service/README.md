# user-service 인수인계서

# 개요

회원 가입, 로그인, 사용자 정보 조회 등 회원 관리 관련 서비스를 담당합니다.

# 디렉터리 구조

src/main/java/io/ssafy/p/k12s101/userservice  
├── UserServiceApplication.java  
├── common // 공통 모듈  
│   ├── config  
│   ├── exception  
│   ├── interceptor  
│   └── util  
├── controller  
│   ├── UserController.java  
│   └── dto  
├── domain // 엔티티 관련  
│   ├── User.java  
│   ├── UserRepository.java  
│   └── UserRole.java  
└── service // 비즈니스 로직  
      ├── ChangeUserPasswordService.java  
      ├── CheckEmailDuplicationService.java  
      ├── FindUserProfileService.java  
      ├── LoginUserService.java  
      ├── RegisterUserService.java  
      ├── SearchUsersService.java  
      ├── UpdateUserProfileService.java  
      ├── dto  
      └── impl  

---

# common 폴더

전역에서 쓰이는 예외 처리 및 인증을 위한 인터셉터 관련 로직을 수행합니다.

Middleware 에서 넘어온 header에서 x-user-id 를 추출, jwt 토큰 관리 등 로직을 수행합니다.

---

# controller

사용자 회원가입, 로그인, 정보 조회 등 사용자 관련 api 호출을 담당합니다.

로그인이 필요한 기능은 x-user-id를 필요로 합니다. (사용자 정보 조회, 정보 수정, 사용자 검색 등)

각 API에 대한 Request/Response 형식은 코드 또는 명세서를 확인해주시기 바랍니다.

---

# domain

데이터베이스에 저장되는 User 엔티티를 정의합니다.

UserRole은 일반 사용자인 USER, 관리자인 ADMIN으로 나뉩니다.

---

# service

비즈니스 메인 로직을 담당합니다.

repository를 호출하여 DB 데이터 CRUD를 수행합니다.

- LoginUserServiceImpl
    - 이메일로 사용자를 조회하고, 비밀번호 검증 후 JWT 토큰을 생성합니다.
- RegisterUserServiceImpl
    - 이메일 중복을 확인한 뒤, 새 사용자 정보를 저장합니다.
    - 비밀번호는 해싱하여 저장하고, 기본 권한은 `USER`로 설정됩니다.
- FindUserProfileServiceImpl
    - 사용자 ID로 정보를 조회하여 이름, 이메일, 부서, 역할을 반환합니다.
- UpdateUserProfileServiceImpl
    - 사용자 ID로 사용자를 조회하고 이름, 부서를 수정합니다.
- ChangeUserPasswordServiceImpl
    - 현재 비밀번호가 일치하는지 검증 후, 새 비밀번호로 변경합니다.
- CheckEmailDuplicationServiceImpl
    - 입력된 이메일이 DB에 존재하는지 확인합니다.
    - 존재하지 않으면 사용 가능한 이메일로 판단합니다.
- SearchUsersServiceImpl
    - 이름으로 사용자 목록을 페이징하여 조회합니다.
    - 이름이 없으면 전체 사용자 조회, 있으면 LIKE 연산을 수행합니다.
