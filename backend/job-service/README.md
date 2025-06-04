# job-service 인수인계서

---

# 개요

Main 페이지에서 사용자가 생성하는 job에 대한 생성, Job Management 페이지에서의 조회, 스케줄 생성을 위한 Job 조회 등 Job과 관련된 CRUD 로직을 수행합니다.

# 디렉토리 구조

job-service/  
└── app/  
├── api/         # 라우터 (엔드포인트 정의)  
├── core/        # 공통 유틸리티  
├── crud/        # 데이터베이스 조작 함수  
├── db/          # DB 연결 설정  
├── models/      # 모델(엔티티) 정의  
├── schemas/     # Pydantic 스키마 (요청/응답 객체)  
└── services/    # 비즈니스 로직 (api와 crud 사이 역할)  

---

# models/models.py

### 주요 기능

DB 테이블과 매핑되는 모델 클래스 정의합니다.

### 상세

- Job
    - 테이블 명 : jobs
    - 사용자 정보, job 정보, job 생성 시 입력한 데이터 관련 정보, job 실행 코드 등을 저장 및 관리합니다.
    - JobSourceData와 1:1
    - JobCommand와 1:N
- JobSourceData
    - 테이블 명 : job_source_data
    - job 생성 시 불러온 데이터 관련 파라미터를 저장합니다.
- JobCommand
    - 테이블 명 : job_commands
    - job 생성 시 사용자가 입력한 커맨드 저장합니다.

---

# api/job_api.py

### 주요 기능

Job 관련 REST API 엔드포인트 지정합니다.

사용자 인증을 위해, `auth.get_user_id_from_header` 메서드에 의존합니다.

비즈니스 로직은 `job_service` 로 위임하였습니다.

### 상세

```python
@router.post("")
def create_job
job을 생성합니다.

@router.get("")
def get_jobs
job_management 페이지 이동 시 목록 조회를 위해 여러 job을 조회합니다.

@router.get("/{job_id}")
def get_job_detail
특정 job에 대한 상세 정보를 조회합니다.

@router.put("/{job_id}")
def update_job
특정 job을 수정합니다.

@router.delete("/{job_id}")
def delete_job
특정 job을 삭제합니다.

@router.post("/for-schedule")
def get_jobs_for_creating_schedule
스케줄 생성을 위한 job 조회 시 사용됩니다.

@router.post("/for-schedule/commands")
def get_jobs_with_commands_for_creating_schedule
스케줄 생성을 위한 job 조회 시 사용되며, 함께 저장된 커맨드까지 반환합니다.
```

---

# schemas/*_schema.py

### job_create_schema.py

job 생성 시 필요한 schema입니다.

Request에는 job 생성 시 사용자가 입력한 정보가 담겨있습니다.

Response의 경우 다음의 양식을 따릅니다.

날짜는 str 로 선언합니다.

```json
{
  "result" : "string",
  "data" : {
    "job_id": "string",
    "created_at" : "ISO-8601"
  }
}
```

### job_delete_schema.py

job 삭제 시 필요한 schema입니다.

Response는 다음의 양식을 따릅니다.

```json
{
  "result" : "string",
  "data" : null
}
```

### job_detail_schema.py

job 조회 시 사용되는 schema 입니다.

Request의 경우, 쿼리 파라미터로 여러 값을 전달받으며, 그 중 mine의 값은 필수이지만, 그 외 값들은 nullable 합니다.

Response의 경우, 다음의 양식을 따릅니다.

날짜는 str 로 선언합니다.

```json
{
  "result": "string",
  "data": {
    "jobs": [{
      "id": "string",
      "user_name": "string",
      "type": "string",
      "title": "string",
      "description": "string",
      "data_load_command": "string",
      "data_load_url": "string",
      "source_data": { // source data의 값들은 nullable합니다.
        "factory_name": "string",
        "system_name": "string",
        "metric": "string",
        "factory_id": "string",
        "product_code": "string",
        "start_date": "ISO-8601",
        "end_date": "ISO-8601"
      },
      "commands": [{
        "content": "string",
        "order": 1
      }],
      "code": "string",
      "created_at": "ISO-8601" 
    }],
    "page": int,
    "size": int,
    "total": int
  }
}
```

### job_for_schedule_schema.py

스케줄 생성 시 필요한 job을 조회할 때 사용되는 schema입니다.

Request는 다음의 양식을 따릅니다.

```json
"job_ids": [int, int, int, ...]
```

Response는 다음의 양식을 따릅니다.

```json
{
    "result": "success",
    "data": {
      "jobs": [
        {
          "id": "string",
          "title": "string",
          "description": "string",
          "code": "string",
          "data_load_code": "string",
          "data_load_url": "string",
          "commands": [ // commands의 경우 호출되는 api에 따라 생략될 수 있습니다.
            "content": "string",
            "order": 1
          ]
        }
      ]
    }
}
```

---

### job_list_schema.py

job_management 페이지에서 목록 조회 시 사용되는 schema입니다.

Response는 다음의 양식을 따릅니다.

```json
{
    "result": "success",
    "data": {
      "jobs": [{
        "id": "string",
        "type": "string",
        "user_name": "string",
        "title": "string",
        "description": "string",
        "data_load_command": "string",
        "data_load_url": "string",
        "commands": [{
          "content": "string",
          "order": 1
        }],
        "code": "string",
        "created_at": "ISO-8601"
      }],
      "page": 1,
      "size": 10,
      "total": 100
}
```

---

### job_update_schema.py

job 수정 시 사용되는 schema입니다.

Request는 다음의 양식을 따릅니다.

```json
{
  "type": "string",
  "title": "string",
  "description": "string",
  "data_load_command": "string",
  "data_load_url": "string",
  "data_load_code": "string", // nullable
  "commands": ["string", "string", ...],
  "code": "string"
}
```

Response는 다음의 양식을 따릅니다. (overwrite 방식이라 실제로는 미사용)

```json
{
  "result" : "string",
  "data" : {
    "job_id": "string",
    "updated_at" : "ISO-8601"
  }
}
```

---

# services/job_service.py

job_api에서 호출되는 모든 비즈니스 로직을 담당합니다.

### 주의

job update 시, 덮어쓰는 것이 아닌 새로운 job을 생성합니다. 때문에 update_job에서 create_job을 호출합니다.

job 목록 조회의 경우, job_management 페이지에서 관리자만이 다른 사용자의 job 목록을 조회할 수 있습니다. 해당 api 호출 시 관리자인지 확인 후 처리합니다. 또한, 다양한 쿼리 파라미터를 통해 필터링을 수행합니다.

---

# db/database.py

데이터베이스와 연결을 담당합니다.

데이터베이스의 정보는 .env 파일로 관리합니다.

---

# crud/crud.py

job_service.py에서 호출되어, 데이터베이스에 접근하여 데이터를 다루는 작업을 수행합니다.

---

# core/auth.py

사용자 정보 조회를 위해, User-Service의 api를 호출합니다.

Middleware를 통해 헤더로 넘어오는 x-user-id 를 추출하며, 사용자의 이름, 부서, 권한 등을 확인하기 위해 User-Service를 통해 데이터를 조회합니다.
