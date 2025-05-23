from app.core import auth
from app.db.database import get_db
from app.schemas.job_create_schema import JobCreateRequest
from app.schemas.job_detail_schema import JobDetailRequest
from app.schemas.job_for_schedule_schema import JobForScheduleRequest
from app.schemas.job_update_schema import JobUpdateRequest
from app.services import job_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

router = APIRouter(
    prefix="/api/jobs",
    dependencies=[Depends(auth.get_user_id_from_header)]
)

@router.post("")
def create_job(request: JobCreateRequest, db: Session = Depends(get_db), user_id: int = Depends(auth.get_user_id_from_header)) -> JSONResponse:
    return job_service.create_job(request, user_id, db)

@router.get("")
def get_jobs(
        db:Session = Depends(get_db),
        request: JobDetailRequest = Depends(),
        user_id: int = Depends(auth.get_user_id_from_header)
) -> JSONResponse:
    return job_service.get_jobs(db, request, user_id)

@router.get("/{job_id}")
def get_job_detail(job_id: str, db: Session = Depends(get_db)) -> JSONResponse:
    return job_service.get_job_detail(job_id, db)

@router.put("/{job_id}")
def update_job(
        job_id: str,
        request: JobUpdateRequest,
        db: Session = Depends(get_db),
        user_id: int = Depends(auth.get_user_id_from_header)
) -> JSONResponse:
    return job_service.update_job(db, job_id, request, user_id)


@router.delete("/{job_id}")
def delete_job(
        job_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(auth.get_user_id_from_header)
):
    return job_service.delete_job(db, job_id, user_id)

# Schedule-Service에서 스케줄 생성에 필요한 Job 데이터를 반환합니다.
# 필요한 Job의 id들이 배열 형태로 들어옵니다.
@router.post("/for-schedule")
def get_jobs_for_creating_schedule(request: JobForScheduleRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return job_service.get_jobs_for_creating_schedule(request, db)

# 스케줄 생성 시 필요한 Job 데이터에 command 까지 포함하여 반환합니다.
@router.post("/for-schedule/commands")
def get_jobs_with_commands_for_creating_schedule(request: JobForScheduleRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return job_service.get_jobs_with_commands_for_creating_schedule(request, db)