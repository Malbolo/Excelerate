import logging
import math
import requests
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.crud import crud
from app.models import models
from app.schemas import job_detail_schema, job_list_schema
from app.schemas.job_create_schema import JobCreateRequest
from app.schemas.job_detail_schema import JobDetailResponse
from app.schemas.job_update_schema import JobUpdateRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_info(user_id: int):
    url = "http://user-service.user-service.svc.cluster.local:8080/api/users/me/profile"
    headers = {
        "x-user-id": str(user_id)
    }

    response = requests.get(url, headers=headers)
    logger.info(response.json())

    if response.status_code == 200:
        user_data = response.json()
        name = user_data.get("data").get("name")
        department = user_data.get("data").get("department")
        role = user_data.get("data").get("role")
        logger.info("name : %s", name)
        logger.info("department : %s", department)
        logger.info("role : %s", role)

        return {
            "name": name,
            "department": department,
            "role": role
        }
    else:
        return None

async def create_job(request: JobCreateRequest, user_id: int, db: Session) -> JSONResponse:
    try:
        user_info = get_user_info(user_id)

        await crud.create_job(db, request, user_id, user_info.get("name"), user_info.get("department"))
        return JSONResponse(status_code=200, content={"message": "Job이 생성되었습니다."})
    except Exception as e:
        logger.error(f"Failed to create job for user_id {user_id}: {e}", exc_info=True)  # 에러 로그 (예외 정보 포함)
        return JSONResponse(status_code=500, content={"message": "Job이 생성에 실패하였습니다."})

async def get_job_detail(id: int, db: Session) -> JSONResponse:
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = job_detail_schema.create_job_detail_schema(job)

    return JSONResponse(content=JobDetailResponse(result="success", data=job_data).dict())

async def update_job(db: Session, job_id: int, job_request: JobUpdateRequest, user_id: int):
    return crud.update_job(db, job_id, job_request, user_id)

def delete_job(db: Session, job_id: int, user_id: int):
    return crud.delete_job(db, job_id, user_id)

def get_filtered_query(db: Session, mine: bool, name: Optional[str], dep: Optional[str], title: Optional[str], user_id: int):
    query = db.query(models.Job)
    if mine:
        query = query.filter(models.Job.user_id == user_id)
    else:
        user_info = get_user_info(user_id)
        if user_info is None or user_info.get("role") != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="접근 권한이 없습니다. (관리자만 접근 가능)"
            )

        if name:
            query = query.filter(models.Job.user_name == name)
        else:
            raise HTTPException(
                status_code=404,
                detail="조회할 사용자를 입력해주세요."
            )
        if dep:
            query = query.filter(models.Job.user_department == dep)

    if title:
        query = query.filter(models.Job.title.ilike(f"%{title}%"))

    return query


def get_jobs(db: Session, mine: bool, name: Optional[str], dep: Optional[str], page: Optional[int], size: Optional[int], title: Optional[str], user_id: int):
    query = get_filtered_query(db, mine, name, dep, title, user_id)

    if size:
        total = math.ceil(query.count() / size)
    else:
        total = 1

    if page is not None and size is not None:
        jobs = query.offset((page - 1) * size).limit(size).all()
    else:
        jobs = query.all()

    job_data = [job_detail_schema.create_job_detail_schema(job) for job in jobs]

    return JSONResponse(content=job_list_schema.JobListResponse(
        result="success",
        data={
            "jobs": job_data,
            "page": page,
            "size": size,
            "total": total
        }).dict())
