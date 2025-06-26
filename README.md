# ⚡️ Excelerate
사내 보고서 업무를 더 빠르게, 생성형 AI 기반 보고서 자동화 시스템, Excelerate ⚡️  
삼성전자 생산기술연구소와 협업한 프로젝트로, 해외 법인 실무에 단계적으로 도입될 예정입니다.

## 🚀 주요 기능
### ➊ 자연어 기반 보고서 업무 수행
- 자연어 기반 명령어 입력
  - 명령어 순서 변경, 수정, 삭제 지원
  - 하나의 명령어 묶음을 Job으로 저장
- 코드 자동 생성 및 실행
  - 외부 문서 및 데이터 기반 RAG 적용
  - LLM이 명령어를 해석하고 관련 정보를 검색하여 코드 작성 및 실행
  - 실행 결과를 데이터프레임 형태로 시각화
- 실시간 작업 로그 제공
  - LLM Chain 단계별 실시간 로그 출력
  - 실행 과정 및 에러 로그 투명하게 확인 가능

|Main|
|:--:|
|<img width="1440" alt="Image" src="https://github.com/user-attachments/assets/e2d8f291-fa8f-4f1c-af4f-861f3caa7cb3" />|

### ➋ 보고서 업무 관리
- 저장된 보고서 업무 관리
  - 기존에 저장한 보고서 업무 목록 제공
  - 보고서 업무의 수정, 삭제, 재실행 가능

|Job Management|
|:--:|
|<img width="1440" alt="Image" src="https://github.com/user-attachments/assets/3d41d43f-0546-4581-96ec-316380f4045b" />|

### ➌ 보고서 업무 스케줄링 자동화
- 여러 Job을 묶어 하나의 스케줄로 관리
- Airflow 기반 스케줄링 시스템 적용
- 다양한 스케줄 뷰 제공
  - 달력(Calendar) 뷰 : 스케줄 실행 일정을 직관적으로 확인
  - 칸반(Kanban) 뷰 : 스케줄 진행 상태를 단계별로 관리
- 스케줄 단위 기능
  - 주기적 자동 실행 (daily, weekly, monthly)
  - 단위 실행
  - 수정, 삭제
  - 일시정지 및 재개
- 실패 구간 및 에러 로그 확인
  - 스케줄 실행 실패 시, 어느 Job 또는 단계에서 실패했는지 표시
  - 상세 에러 로그 제공으로 원인 파악 용이

|Scheduler Management|Scheduler Monitoring|
|:--:|:--:|
|<img width="1440" alt="Image" src="https://github.com/user-attachments/assets/cb68c055-c152-4bf7-8c92-4c85e2c0f080" />|<img width="1440" alt="Image" src="https://github.com/user-attachments/assets/ac1b5989-9a90-4ebe-9751-012ed0feca0d" />|

### ➍ 생성형 AI 입출력 모니터링 & 프롬프트 실험 및 외부 문서 기반 AI 응답 테스트
- 생성형 AI 입출력 모니터링
  - LLM 입력과 출력 이력 실시간 확인
  - 히스토리 관리 및 검색 기능 제공
- 프롬프트 실험 환경 제공
  - 다양한 프롬프트를 실시간으로 테스트 가능
  - Few-shot 수정 및 관리 지원
- 외부 문서 기반 AI 응답 테스트
  - 외부 문서 및 데이터 기반 RAG(Retrieval-Augmented Generation) 구조 적용
  - 문서 업로드 및 삭제 지원

|Agent Monitoring|Rag Studio|
|:--:|:--:|
|<img width="1440" alt="Image" src="https://github.com/user-attachments/assets/e16fee27-1266-48a3-b4fd-5199ec530cc4" />|<img width="1440" alt="Image" src="https://github.com/user-attachments/assets/fe31cdea-f59b-407c-89f1-c2e9350949e5" />|

## 🧩 아키텍처
![아키텍처.png](./docs/아키텍처.png)

### 각 Service 별 설명
[Job Service README 보기](backend/job-service/README.md)

[Auth Service README 보기](backend/auth-service/README.md)

[User Service README 보기](backend/user-service/README.md)

[Schedule Service README 보기](backend/schedule-service/README.md)

### 배포 가이드
[배포 및 운영 가이드](exec/배포 및 운영 가이드.pdf)
