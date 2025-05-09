from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import models
from app.models.models import JobCommand, Job
from app.schemas.job.job_create_schema import JobCreateRequest
from app.schemas.job.job_update_schema import JobUpdateRequest


async def create_job(db: Session, job: JobCreateRequest, user_id: int, user_name: str, department: str):
    db_job = models.Job(
        user_id=user_id,
        user_name=user_name,
        user_department=department,
        type=job.type,
        title=job.title,
        description=job.description,
        data_load_command=job.data_load_command,
        data_load_url=job.data_load_url,
        code=job.code
    )
    db.add(db_job)
    db.flush()
    for idx, command in enumerate(job.commands):
        db_command = models.JobCommand(content=command, order=idx + 1, job=db_job)
        db.add(db_command)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, job_id: int, job_request: JobUpdateRequest, user_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    job.type = job_request.type
    job.name = job_request.name
    job.description = job_request.description
    job.data_load_command = job_request.data_load_command
    job.data_load_url = job_request.data_load_url
    job.code = job_request.code
    job.updated_at = datetime.utcnow()

    # 기존 job_commands 삭제
    db.query(JobCommand).filter(JobCommand.job_id == job.id).delete()

    # 새로운 job_commands 추가
    for idx, command_text in enumerate(job_request.commands):
        command = JobCommand(content=command_text, order=idx, job_id=job.id)
        job.commands.append(command)

    db.commit()
    db.refresh(job)

    return {
        "result": "success",
        "data": {
            "job_id": job.id,
            "updated_at": job.updated_at.isoformat()
        }
    }


def delete_job(db: Session, job_id: int, user_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    db.delete(job)
    db.commit()

    return {"result": "success", "data": None}


def get_job_by_id(db: Session, job_id: str):
    """
    DB에서 job_id로 job 정보를 조회
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        return {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "type": job.type,
            "user_id": job.user_id,
            "user_name": job.user_name,
            "user_department": job.user_department,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }
    except Exception as e:
        print(f"Error fetching job from DB: {str(e)}")
        return None
