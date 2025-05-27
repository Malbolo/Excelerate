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
        # User-Service API를 호출하여 사용자 정보를 조회합니다.
        user_info = auth.get_user_info(user_id)

        # Job을 생성합니다.
        job = crud.create_job(db, request, user_id, user_info.get(USER_NAME), user_info.get(USER_DEPARTMENT))

        # 응답 데이터 구성
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
        # job_id를 이용해 Job을 조회
        job = crud.get_job_by_id(db, job_id)

        # Job 데이터를 스키마 형태로 변환
        job_data = JobDetailSchema.create(job)

        # 성공 응답 반환
        response = JobDetailResponse(result=SUCCESS, data=job_data)
        return JSONResponse(content=response.dict())

    except NoResultFound:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)

    except Exception as e:
        logger.debug(f"Getting A Job Detail Failed: {e}")
        response = JobDetailResponse(result=FAIL, data=None)
        return JSONResponse(content=response.dict())


def update_job(db: Session, job_id: str, request: JobUpdateRequest, user_id: int):
    # Job을 수정합니다.
    # 이때, 기존 job을 조회 후, updated_at 컬럼만 현재 시간으로 수정 후, 새로운 job을 생성합니다. (Overwrite X)
    updated_job = crud.update_job(db, job_id, request, user_id)

    # 응답 데이터 구성
    data = JobUpdateResponseData(
        job_id=str(updated_job.id),
        updated_at=str(updated_job.updated_at)
    )

    return JobUpdateResponse(
        result=SUCCESS,
        data=data
    )


def delete_job(db: Session, job_id: int, user_id: int):
    # Job을 삭제합니다.
    crud.delete_job(db, job_id, user_id)
    response = JobDetailResponse(result=SUCCESS, data=None)
    return JSONResponse(content=response.dict())


# Job Management에서 목록 조회 시, 필터링 요청한 값에 따라 필터링을 수행합니다.
# 각 값이 존재하면 필터링되고, 존재하지 않으면 필터링되지 않습니다.
def filter_query(request: JobDetailRequest, query):
    # 이름으로 필터링
    if request.name:
        query = query.filter(models.Job.user_name.ilike(f"%{request.name}%"))

    # 부서로 필터링
    if request.dep:
        query = query.filter(models.Job.user_department == request.dep)

    # 타입으로 필터링
    if request.types:
        types = [t.strip() for t in request.types.split(',')]
        query = query.filter(or_(*[models.Job.type == t for t in types]))

    # 제목으로 필터링
    if request.title:
        query = query.filter(models.Job.title.ilike(f"%{request.title}%"))

    return query


# 관리자 권한 여부 확인. 관리자일 경우 True를 반환합니다.
def is_admin_user(user_info):
    if user_info is None or user_info.get(USER_ROLE) != ADMIN_USER:
        return False
    return True

# Job Management에서 필터링된 목록을 조회할 수 있도록 Job을 가져옵니다.
def get_filtered_query(db: Session, request: JobDetailRequest, user_id: int):
    # 전체 Job 리스트를 생성일 기준으로 내림차순 정렬 (최신순 정렬)
    query = crud.get_all_jobs(db).order_by(desc(models.Job.created_at))

    # 쿼리 파라미터로 'mine=True' 라면, 본인의 Job을 조회하는 것이므로 해당하는 Job 만 반환합니다.
    if request.mine:
        query = query.filter(models.Job.user_id == user_id)
    else:
        # 쿼리 파라미터로 'mine=False' 라면, 관리자만이 조회 가능합니다.
        user_info = auth.get_user_info(user_id)
        if not is_admin_user(user_info):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ACCESS_DENIED)

    return filter_query(request, query)


# 전체 페이지 수 계산
def get_total_page_count(query_count: int, size: int):
    if size:
        return math.ceil(query_count / size)
    return 1

# 페이지네이션을 수행합니다.
def paginate_query(query, page: int | None, size: int | None):
    if page is not None and size is not None:
        return query.offset((page - 1) * size).limit(size).all()
    return query.all()

# Job 목록 조회를 수행하며, 필터링, 페이지네이션 결과가 반영됩니다.
def get_jobs(db: Session, request: JobDetailRequest, user_id: int):
    # 필터 조건이 적용된 쿼리 객체를 가져옴
    query = get_filtered_query(db, request, user_id)

    # 총 페이지 수 계산
    total = get_total_page_count(query.count(), request.size)

    # 페이지네이션을 통해 결과 조회
    jobs = paginate_query(query, request.page, request.size)

    # 각 Job 객체를 스키마로 변환
    job_list = [JobDetailSchema.create(job) for job in jobs]

    # 응답 데이터 생성
    response = JobListResponse.create(SUCCESS, job_list, request.page, request.size, total)

    return JSONResponse(content=response.dict())

# Schedule-Service에서 스케줄 생성을 위해 필요한 Job 데이터를 반환합니다.
def get_jobs_for_creating_schedule(request: JobForScheduleRequest, db: Session) -> JSONResponse:
    # 요청한 job_id 리스트로 Job 조회
    jobs = crud.get_jobs_by_ids(request.job_ids, db)

    if not jobs:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)

    # 스케줄 생성을 위한 Job 데이터 구성
    job_list = [JobForSchedule.create(job) for job in jobs]

    response = JobForScheduleResponse(result=SUCCESS, data=JobList(jobs=job_list))
    return JSONResponse(content=response.dict())

# 스케줄 생성 시 필요한 Job 데이터에 command 까지 포함하여 반환합니다.
def get_jobs_with_commands_for_creating_schedule(request: JobForScheduleRequest, db: Session) -> JSONResponse:
    # 요청한 job_id 리스트로 Job 조회
    jobs = crud.get_jobs_by_ids(request.job_ids, db)

    if not jobs:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=JOB_NOT_FOUND)

    # 커맨드 포함 Job 리스트 구성
    job_list = [JobForScheduleWithCommands.create(job) for job in jobs]

    response = JobForScheduleWithCommandsResponse(result=SUCCESS, data=JobListWithCommands(jobs=job_list))
    return JSONResponse(content=response.dict())
