## Airflow에서 엑셀 작업 및 minio 접근이 가능하도록 하는 코드
airflow-scheduler에 다음 패키지들을 설치하고, 이 폴더의 파일들을 airflow의 dags/utils 폴더로 복사해주세요. 다음과 같이 진행하면 됩니다.

### Kubernetes 환경
``` bash
# 필요한 패키지 설치
kubectl exec -it -n schedule-service airflow-scheduler-0 -- bash
pip install minio pydantic-settings openpyxl
```

``` bash
# airflow 내 폴더로 utils 폴더 복사
kubectl cp ./utils schedule-service/airflow-scheduler-0:/opt/airflow/dags/utils
```
