from __future__ import annotations

import math
from http import HTTPStatus

from app.core import auth
from app.core.constants import SUCCESS, FAIL, JOB_NOT_FOUND, ADMIN_USER, USER_ROLE, \
    ACCESS_DENIED
from app.core.constants import USER_DEPARTMENT, USER_NAME
from app.core.log_config import logger
from app.crud import crud
from app.models import models
from app.schemas.job_create_schema import JobCreateRequest, JobCreateResponseData, JobCreateResponse
from app.schemas.job_detail_schema import JobDetailSchema, JobDetailResponse, JobDetailRequest
from app.schemas.job_for_schedule_schema import JobForScheduleRequest, JobForSchedule, JobForScheduleResponse, \
    JobForScheduleWithCommands, JobForScheduleWithCommandsResponse, JobList, JobListWithCommands
from app.schemas.job_list_schema import JobListResponse
from app.schemas.job_update_schema import JobUpdateRequest, JobUpdateResponseData, JobUpdateResponse
from fastapi import HTTPException
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from starlette.responses import JSONResponse


def create_job(request: JobCreateRequest, user_id: int, db: Session) -> JSONResponse:
    try:
        user_info = auth.get_user_info(user_id)
        job = crud.create_job(db, request, user_id, user_info.get(USER_NAME), user_info.get(USER_DEPARTMENT))

        data = JobCreateResponseData(
            job_id=str(job.id),
            created_at=str(job.created_at)
        )
        response = JobCreateResponse(result=SUCCESS, data=data)
        return JSONResponse(content=response.dict())

    except Exception as e:
        logger.debug(f"Job Creation Failed: {e}")
        response = JobCreateResponse(result=FAIL, data=None)
        return JSONResponse(content=response.dict())

def get_job_detail(job_id: str, db: Session) -> JSONResponse:
    try:
        job = crud.get_job_by_id(db, job_id)
        job_data = JobDetailSchema.create(job)

        response = JobDetailResponse(result=SUCCESS, data=job_data)
        return JSONResponse(content=response.dict())
    except NoResultFound:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)
    except Exception as e:
        logger.debug(f"Getting A Job Detail Failed: {e}")
        response = JobDetailResponse(result=FAIL, data=None)
        return JSONResponse(content=response.dict())

def update_job(db: Session, job_id: str, request: JobUpdateRequest, user_id: int):
    updated_job = crud.update_job(db, job_id, request, user_id)

    data = JobUpdateResponseData(
        job_id=str(updated_job.id),
        updated_at=str(updated_job.updated_at)
    )

    return JobUpdateResponse(
        result=SUCCESS,
        data=data
    )

def delete_job(db: Session, job_id: int, user_id: int):
    crud.delete_job(db, job_id, user_id)
    response = JobDetailResponse(result=SUCCESS, data=None)
    return JSONResponse(content=response.dict())

def filter_query(request: JobDetailRequest, query):
    if request.name:
        query = query.filter(models.Job.user_name.ilike(f"%{request.name}%"))
    if request.dep:
        query = query.filter(models.Job.user_department == request.dep)
    if request.types:
        types = [t.strip() for t in request.types.split(',')]
        query = query.filter(or_(*[models.Job.type == t for t in types]))
    if request.title:
        query = query.filter(models.Job.title.ilike(f"%{request.title}%"))
    return query

def is_admin_user(user_info):
    if user_info is None or user_info.get(USER_ROLE) != ADMIN_USER:
        return False
    return True

def get_filtered_query(db: Session, request: JobDetailRequest, user_id: int):
    query = crud.get_all_jobs(db).order_by(desc(models.Job.created_at))
    if request.mine:
        query = query.filter(models.Job.user_id == user_id)
    else:
        user_info = auth.get_user_info(user_id)
        if not is_admin_user(user_info):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ACCESS_DENIED)

    return filter_query(request, query)


def get_total_page_count(query_count: int, size: int):
    if size:
        return math.ceil(query_count / size)
    return 1

def paginate_query(query, page: int | None, size: int | None):
    if page is not None and size is not None:
        return query.offset((page - 1) * size).limit(size).all()
    return query.all()


def get_jobs(db: Session, request: JobDetailRequest, user_id: int):
    query = get_filtered_query(db, request, user_id)

    total = get_total_page_count(query.count(), request.size)

    jobs = paginate_query(query, request.page, request.size)
    job_list = [JobDetailSchema.create(job) for job in jobs]

    response = JobListResponse.create(SUCCESS, job_list, request.page, request.size, total)

    return JSONResponse(content=response.dict())

def get_jobs_for_creating_schedule(request: JobForScheduleRequest, db: Session) -> JSONResponse:
    jobs = crud.get_jobs_by_ids(request.job_ids, db)

    if not jobs:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)
    
    job_list = [JobForSchedule.create(job) for job in jobs]

    response = JobForScheduleResponse(result=SUCCESS, data=JobList(jobs=job_list))

    return JSONResponse(content=response.dict())

def get_jobs_with_commands_for_creating_schedule(request: JobForScheduleRequest, db: Session) -> JSONResponse:
    jobs = crud.get_jobs_by_ids(request.job_ids, db)

    if not jobs:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)

    job_list = [JobForScheduleWithCommands.create(job) for job in jobs]

    response = JobForScheduleWithCommandsResponse(result=SUCCESS, data=JobListWithCommands(jobs=job_list))

    return JSONResponse(content=response.dict())
