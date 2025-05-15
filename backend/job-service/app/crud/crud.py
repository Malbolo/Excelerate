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


def create_job(db: Session, request: JobCreateRequest, user_id: int, user_name: str, department: str):
    db_job = models.Job.create(request, user_id, user_name, department)
    db.add(db_job)
    db.flush()
    for idx, command in enumerate(request.commands):
        db_command = JobCommand(content=command, order=idx + 1, job=db_job)
        db.add(db_command)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job_by_id(db: Session, job_id: str):
    return db.query(models.Job).filter(models.Job.id == job_id).one()

def update_job(db: Session, job_id: str, request: JobUpdateRequest, user_id: int):
    existing_job = get_job_by_id(db, job_id)

    if not existing_job:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=JOB_NOT_FOUND + " or " + ACCESS_DENIED)

    existing_job.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing_job)

    user_info = auth.get_user_info(user_id)
    return create_job(db, request, user_id, user_info.get(USER_NAME), user_info.get(USER_DEPARTMENT))

def get_all_jobs(db: Session):
    return db.query(models.Job).options(joinedload(models.Job.commands))

def delete_job(db: Session, job_id: int, user_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()

    if not job:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=JOB_NOT_FOUND + " or " + ACCESS_DENIED)

    db.delete(job)
    db.commit()

def get_jobs_by_ids(job_ids: List[str], db: Session):
    jobs = db.query(models.Job).filter(models.Job.id.in_(job_ids)).all()
    job_map = {str(job.id): job for job in jobs}

    missing_ids = [job_id for job_id in job_ids if job_id not in job_map]
    if missing_ids:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)

    return [job_map[job_id] for job_id in job_ids]