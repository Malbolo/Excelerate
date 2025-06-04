from datetime import datetime
from http import HTTPStatus
from typing import List

from app.core import auth
from app.core.constants import JOB_NOT_FOUND, ACCESS_DENIED
from app.core.constants import USER_DEPARTMENT, USER_NAME
from app.models import models
from app.models.models import JobCommand, Job
from app.schemas.job_create_schema import JobCreateRequest
from app.schemas.job_update_schema import JobUpdateRequest
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload


# job 생성을 수행합니다.
def create_job(db: Session, request: JobCreateRequest, user_id: int, user_name: str, department: str):
    db_job = models.Job.create(request, user_id, user_name, department)
    db.add(db_job)
    db.flush()

    source_data = request.source_data
    db_source_data = models.JobSourceData(
        job_id=db_job.id,
        factory_name=source_data.factory_name,
        system_name=source_data.system_name,
        metric=source_data.metric,
        factory_id=source_data.factory_id,
        product_code=source_data.product_code,
        start_date=source_data.start_date,
        end_date=source_data.end_date,
    )
    db.add(db_source_data)

    for idx, command in enumerate(request.commands):
        db_command = JobCommand(content=command, order=idx + 1, job=db_job)
        db.add(db_command)

    db.commit()
    db.refresh(db_job)
    return db_job

# id를 통해 단일 job을 가져옵니다.
def get_job_by_id(db: Session, job_id: str):
    return db.query(models.Job) \
        .options(joinedload(models.Job.source_data)) \
        .filter(models.Job.id == job_id) \
        .one()

# id를 통해 job을 조회한 후, 조회된 job은 updated_at만 갱신합니다.
# 이후, 사용자의 Request를 바탕으로 새로운 job을 생성합니다. (Overwrite X)
def update_job(db: Session, job_id: str, request: JobUpdateRequest, user_id: int):
    existing_job = get_job_by_id(db, job_id)

    if not existing_job:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=JOB_NOT_FOUND + " or " + ACCESS_DENIED)

    existing_job.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing_job)

    user_info = auth.get_user_info(user_id)
    return create_job(db, request, user_id, user_info.get(USER_NAME), user_info.get(USER_DEPARTMENT))

# 모든 job을 조회합니다.
def get_all_jobs(db: Session):
    return db.query(models.Job).options(joinedload(models.Job.commands))

# id를 통해 조회하여 삭제를 수행합니다.
def delete_job(db: Session, job_id: int, user_id: int):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=JOB_NOT_FOUND + " or " + ACCESS_DENIED)

    db.delete(job)
    db.commit()

# List에 담긴 id들을 바탕으로 여러 job을 조회합니다.
def get_jobs_by_ids(job_ids: List[str], db: Session):
    jobs = db.query(models.Job).filter(models.Job.id.in_(job_ids)).all()
    job_map = {str(job.id): job for job in jobs}

    missing_ids = [job_id for job_id in job_ids if job_id not in job_map]
    if missing_ids:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)

    # 요청으로 들어온 id들의 순서를 유지합니다.
    return [job_map[job_id] for job_id in job_ids]