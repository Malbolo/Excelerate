from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.core import auth
from app.models import models
from app.models.models import JobCommand, Job
from app.schemas.job.job_create_schema import JobCreateRequest
from app.schemas.job.job_delete_schema import JobDeleteResponse
from app.schemas.job.job_update_schema import JobUpdateRequest, JobUpdateResponseData, JobUpdateResponse


def create_job(db: Session, job: JobCreateRequest, user_id: int, user_name: str, department: str):
    db_job = models.Job.create(job, user_id, user_name, department)
    db.add(db_job)
    db.flush()
    for idx, command in enumerate(job.commands):
        db_command = JobCommand(content=command, order=idx + 1, job=db_job)
        db.add(db_command)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job_by_id(db: Session, job_id: str):
    return db.query(models.Job).filter(models.Job.id == job_id).one()

def update_job(db: Session, job_id: str, job_request: JobUpdateRequest, user_id: int):
    existing_job = get_job_by_id(db, job_id)

    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    existing_job.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing_job)

    user_info = auth.get_user_info(user_id)
    return create_job(db, job_request, user_id, user_info.get("name"), user_info.get("department"))

def get_all_jobs(db: Session):
    return db.query(models.Job).options(joinedload(models.Job.commands))

def delete_job(db: Session, job_id: int, user_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    db.delete(job)
    db.commit()

    response = JobDeleteResponse(result="success", data=None)

    return response

def get_jobs_by_ids(job_ids: List[str], db: Session):
    return db.query(models.Job).filter(models.Job.id.in_(job_ids)).all()
