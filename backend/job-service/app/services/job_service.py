from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.crud import crud
from app.db.database import get_db
from app.models import models
from app.schemas.job_create_schema import JobCreateRequest
from app.schemas.job_update_schema import JobUpdateRequest


async def create_job(request: JobCreateRequest, user_id: int) -> JSONResponse:
    db = next(get_db())
    try:
        crud.create_job(db, request, user_id)
        return JSONResponse(status_code=200, content={"message": "Job이 생성되었습니다."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Job이 생성에 실패하였습니다."})

async def get_job_detail(id: int, db: Session) -> JSONResponse:
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = {
        "id": job.id,
        "type": job.type,
        "title": job.name,
        "description": job.description,
        "data_load_command": job.data_load_command,
        "data_load_url": job.data_load_url,
        "commands": [
            {"content": cmd.content, "order": cmd.order}
            for cmd in sorted(job.commands, key=lambda x: x.order)
        ],
        "code": job.code
    }

    return JSONResponse(content={
        "result": "success",
        "data": job_data
    })

async def get_own_jobs(
    db: Session,
    user_id: int,
    page: Optional[int],
    size: Optional[int],
    title: Optional[str]
) -> JSONResponse:
    query = db.query(models.Job).filter(models.Job.user_id == user_id)

    if title:
        query = query.filter(models.Job.name.ilike(f"%{title}%"))

    total = query.count()

    if page is not None and size is not None:
        jobs = query.offset((page - 1) * size).limit(size).all()
    else:
        jobs = query.all()

    job_data = [
        {
            "id": job.id,
            "type": job.type,
            "title": job.name,
            "description": job.description,
            "data_load_command": job.data_load_command,
            "data_load_url": job.data_load_url,
            "commands": [
                {"content": cmd.content, "order": cmd.order}
                for cmd in sorted(job.commands, key=lambda x: x.order)
            ],
            "code": job.code
        }
        for job in jobs
    ]

    return JSONResponse(content={
        "result": "success",
        "data": {
            "jobs": job_data,
            "page": page,
            "size": size,
            "total": total
        }
    })

async def update_job(db: Session, job_id: int, job_request: JobUpdateRequest, user_id: int):
    return crud.update_job(db, job_id, job_request, user_id)

def delete_job(db: Session, job_id: int, user_id: int):
    return crud.delete_job(db, job_id, user_id)

def get_jobs_by_user(db: Session, user_id: int, page: int, size: int):
    jobs, total_jobs = crud.get_jobs_by_user(db, user_id, page, size)
    return {
        "jobs": [{"id": job.id, "title": job.name, "description": job.description} for job in jobs],
        "page": page,
        "size": size,
        "total": total_jobs
    }