# 🗓️ Scheduler Service

FastAPI 기반의 **스케줄 관리 마이크로서비스**입니다.  
사용자가 정의한 Job들을 조합하여 DAG로 구성하고, Airflow에 등록/실행/조회/삭제하는 기능을 제공합니다.

---

## 📚 목차

- [📁 프로젝트 구조](#-프로젝트-구조)
- [📌 엔드포인트 구조](#-엔드포인트-구조)
- [1. 환경 변수 설정](#1-환경-변수-설정)
- [🧠 주요 기능](#-주요-기능)
- [🧩 연동 서비스](#-연동-서비스)
- [⚙️ 개발 스택](#️-개발-스택)
- [🙋‍♂️ 참고 사항](#️-참고-사항)
- [🧠 DAG 코드 생성 방식](#-dag-코드-생성-방식)
- [📡 Airflow REST API 사용 내역](#-airflow-rest-api-사용-내역)
- [📌 필드 제한 관련 안내](#-필드-제한-관련-안내)
- [🔄 DAG 등록 및 동기화 방식](#-dag-등록-및-동기화-방식)
- [🛡️ 스케줄 등록 유효성 검사](#-스케줄-등록-유효성-검사)

---

## 📁 프로젝트 구조

```
scheduler-service/
├── Dockerfile                     # FastAPI 앱을 위한 Docker 설정
├── requirements.txt              # 프로젝트 의존성 명시
├── scheduler-service.env         # 환경 변수 설정 파일 (.env)
├── .gitignore                    # Git 추적 제외 파일 목록
└── app/
    ├── main.py                   # FastAPI 애플리케이션 진입점
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   └── schedule_api.py       # 스케줄 관련 API 라우터 정의
    ├── core/
    │   ├── __init__.py
    │   ├── auth.py               # 인증/인가 관련 유틸 (ex. JWT 검사)
    │   ├── config.py             # 설정값 및 환경 변수 로드
    │   └── log_config.py         # 로거 설정
    ├── schemas/
    │   ├── __init__.py
    │   └── schedule_schema.py    # 요청/응답용 Pydantic 스키마 정의
    ├── services/
    │   ├── __init__.py
    │   ├── airflow_client.py     # Airflow API 통신 클라이언트
    │   ├── calendar_service.py   # 월별 실행 통계 생성 및 캐싱 로직
    │   ├── dag_service.py        # DAG 코드 생성 및 템플릿 로직
    │   └── schedule_service.py   # 전체 스케줄 관리 및 응답 처리
    └── utils/
        ├── __init__.py
        ├── cron_utils.py         # cron 표현식 유효성 검사
        ├── date_utils.py         # UTC 기준 날짜 처리 함수 모음
        ├── error_utils.py        # 공통 예외 처리 및 표준 응답 생성
        ├── log_utils.py          # 로그 파싱 및 에러 메시지 추출
        └── redis_calendar.py     # Redis 기반 월별 통계 캐시 모듈
```

---

## 📌 엔드포인트 구조

모든 엔드포인트는 `prefix: /api/schedules` 를 가지며, 주요 API는 다음과 같은 경로와 기능으로 구성됩니다.

### ✅ 스케줄 생성 및 수정

- `POST /api/schedules`  
  새 스케줄(DAG)을 생성합니다.

- `PATCH /api/schedules/{schedule_id}`  
  기존 스케줄을 수정합니다.

### 📄 스케줄 상세 및 삭제

- `GET /api/schedules/{schedule_id}`  
  특정 스케줄의 상세 정보를 조회합니다.

- `DELETE /api/schedules/{schedule_id}`  
  특정 스케줄을 삭제합니다.

### 📊 스케줄 실행 통계

- `GET /api/schedules/statistics/monthly?year=YYYY&month=MM`  
  해당 월의 스케줄 실행 통계를 달력 형식으로 조회합니다.

- `DELETE /api/schedules/statistics/monthly/cache?year=YYYY&month=MM`  
  특정 월의 캐시된 통계 데이터를 삭제합니다.

- `GET /api/schedules/statistics/daily?year=YYYY&month=MM&day=DD`  
  특정 날짜의 스케줄 실행 내역을 조회합니다.

### ▶️ 스케줄 실행/상태

- `POST /api/schedules/{schedule_id}/start`  
  스케줄을 수동으로 실행합니다.

- `PATCH /api/schedules/{schedule_id}/toggle`  
  스케줄을 활성화/비활성화합니다.

### 📜 실행 이력

- `GET /api/schedules/{schedule_id}/runs`  
  스케줄 실행 이력(페이징 포함)을 조회합니다.

- `GET /api/schedules/{schedule_id}/runs/{run_id}`  
  특정 실행(run)의 상세 정보 및 작업별 로그를 조회합니다.

### 📚 전체 스케줄 목록

- `GET /api/schedules`  
  전체 스케줄 목록을 필터링 및 페이징 형태로 조회합니다.  
  (파라미터: `title`, `owner`, `frequency`, `status`, `page`, `size`)

---

## 1. 환경 변수 설정

`.env` 또는 `scheduler-service.env` 파일을 준비합니다:

```env
USER_SERVICE_URL=http://user-service:8080/api/users/me/profile
JOB_SERVICE_URL=http://job-service:8000

AIRFLOW_API_URL=http://airflow-webserver:8080/api/v1
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
AIRFLOW_DAGS_PATH=/opt/airflow/dags

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=1
REDIS_CALENDAR_CACHE_TTL=86400
```

---

## 🧠 주요 기능

| 기능 | 설명 |
|------|------|
| ✅ 스케줄 생성 | Job 리스트와 주기 정보를 기반으로 DAG 코드 자동 생성 |
| 🌀 DAG 등록 | DAG 코드는 Airflow DAG 경로에 `.py` 파일로 저장됨 |
| 🔁 스케줄 실행 | 수동 실행 (trigger) 기능 제공 |
| 📊 월별/일별 통계 | Redis 기반 통계 캐싱 (성공/실패/대기/진행 수치) |
| ❌ DAG 삭제 및 토글 | Airflow API + DAG 파일 시스템 삭제 |
| 🔍 실행 이력 및 로그 | Task 실행 로그에서 에러 메시지/트레이스 추출 |

---

## 🧩 연동 서비스

| 서비스 | 역할 | 비고 |
|--------|------|------|
| Airflow | DAG 실행 | REST API 및 DAG 폴더 접근 필요 |
| Redis | 월별 조회 캐시 | TTL 설정 가능 |
| User Service | 사용자 인증 | x-user-id 헤더 기반 |
| Job Service | Job 상세 조회 | DAG Task 코드 생성에 활용 |

---

## ⚙️ 개발 스택

- **Python** 3.11  
- **FastAPI** + Uvicorn  
- **Airflow** REST API  
- **Redis**  
- **Docker**

---

## 🙋‍♂️ 참고 사항

- DAG 코드가 저장되는 `/opt/airflow/dags` 경로는 Airflow와 공유되는 경로입니다.
- Redis는 현재 dev 환경에서는 agent-service의 Redis를 사용하며, 운영 환경에서는 별도 구성할 수 있습니다.

---

## 🧠 DAG 코드 생성 방식

DAG는 사용자가 스케줄을 등록할 때마다 Python 코드 문자열로 자동 생성되어 Airflow의 DAG 폴더에 저장되며, 실행 가능합니다.

DAG 코드 생성을 위한 핵심 로직은 다음 메서드 내부에 구현되어 있습니다:

```python
@staticmethod
def _generate_dag_code(...)
```

> 📍 위치: `scheduler-service/app/services/schedule_service.py`

### 주요 기능

- DAG 실행 시 이메일 알림 전송 (성공/실패 여부에 따라 다르게 발송)
- 각 Job 마다 다음과 같은 태스크들이 자동 생성됨:
  - `PythonOperator`: 사용자 코드 실행
  - `BranchPythonOperator`: 결과 파일 존재 여부에 따라 이메일 전송 여부 판단
  - `EmailOperator`: 엑셀 파일을 첨부하여 결과 이메일 발송
  - `DummyOperator`: 이메일을 생략할 경우 건너뛰기 처리
  - `PythonOperator`: 작업 결과 파일 및 임시 디렉토리 정리
- DAG 전체 완료 후:
  - 하나라도 실패한 경우 실패 감지 태스크 실행
  - 모든 태스크가 종료되면 상태 알림 이메일 발송

### 커스터마이징 포인트

- DAG 태스크 구성 순서를 바꾸거나 조건 분기 로직을 조정할 수 있습니다.
- 알림 이메일의 템플릿 문구, 수신자 등을 변경할 수 있습니다.
- 사용자 코드 실행 방식 (입력/출력 구조 등)을 변경하거나, 추가 로깅을 삽입할 수 있습니다.
- `data_load_code`의 전처리 로직, URL 변환 방식 등을 수정할 수 있습니다.

➡️ DAG 구성이나 태스크 로직을 수정하고 싶다면  
`schedule_service.py` 내 `_generate_dag_code(...)` 메서드를 수정하면 됩니다.

---

## 📡 Airflow REST API 사용 내역

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET    | /dags | DAG 목록 조회 |
| GET    | /dags/{dag_id} | 특정 DAG 상세 정보 조회 |
| POST   | /dags/{dag_id}/dagRuns | DAG 실행 트리거 |
| GET    | /dags/{dag_id}/dagRuns | DAG 실행 이력 목록 조회 |
| GET    | /dags/{dag_id}/dagRuns/{dag_run_id} | DAG 실행 이력 상세 조회 |
| DELETE | /dags/{dag_id}/dagRuns/{dag_run_id} | DAG 실행 이력 삭제 |
| GET    | /dagRuns | 모든 DAG 실행 이력 전체 조회 |
| GET    | /dagRuns/{dag_run_id}/taskInstances | 특정 DAG 실행의 태스크 인스턴스 목록 |
| GET    | /dags/{dag_id}/tasks | DAG 내 태스크 정의 목록 조회 |
| PATCH  | /dags/{dag_id} | DAG의 상태 변경 (예: pause/unpause) |
| POST   | /dags/{dag_id}/clearTaskInstances | DAG 태스크 인스턴스 클리어 |

---

## 📌 필드 제한 관련 안내

- 일부 API는 `fields` 파라미터를 사용해 원하는 필드만 응답받도록 할 수 있습니다.
- 예시:
  ```
  GET /dags?limit=50&offset=0&fields=dag_id,description,tags,is_paused
  ```
- 성능상 이점이 있으나, 추가 정보가 필요하다면 `fields`를 제거하거나 수정하세요.

---

## 🔄 DAG 등록 및 동기화 방식

- 생성된 DAG 코드는 `.py` 파일로 변환되어 `AIRFLOW_DAGS_PATH` (기본값: `/opt/airflow/dags`) 경로에 저장됩니다.
- 해당 경로는 Airflow 컨테이너와 **볼륨 마운트로 공유**되어, 코드 변경 즉시 자동으로 반영됩니다.
- Airflow의 주기적인 DAG 스캔 주기에 따라 신규 DAG가 인식됩니다.
- 실시간 등록을 위해 DAG 저장 후 `/dags/{dag_id}`를 조회하여 존재 여부를 확인합니다.

---

## 🛡️ 스케줄 등록 유효성 검사

스케줄 등록 시 다음과 같은 유효성 검사 및 방어 로직이 포함되어 있습니다:

- **Cron 표현식 유효성 검사**  
  - `croniter` 라이브러리를 사용해 주기 설정이 유효한지 사전 확인합니다.

- **날짜 범위 확인**  
  - `start_date`는 과거 날짜를 허용하되, `end_date`가 있다면 `start_date`보다 이후여야 합니다.

- **Job 중복 검사 및 유효성 확인**  
  - Job ID, 코드 및 URL 필드가 존재하는지 확인하며, 존재하지 않거나 중복될 경우 에러를 반환합니다.

- **에러 발생 시**  
  - `ValidationError`, `ServiceError` 등의 커스텀 예외 클래스를 통해 일관된 에러 응답을 제공합니다.

```json
{
  "result": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "cron 표현식이 유효하지 않습니다."
  }
}
```

