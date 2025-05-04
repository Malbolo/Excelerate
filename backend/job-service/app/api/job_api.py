from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.db.database import get_db
from app.schemas.job_create_schema import JobCreateRequest
from app.schemas.job_update_schema import JobUpdateRequest
from app.services import job_service

router = APIRouter(
    prefix="/api/jobs"
)


@router.post("")
async def create_job(request: Request, job_request: JobCreateRequest) -> JSONResponse:
    user_id = request.headers.get("x-user-id")
    print(user_id)
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})

    return await job_service.create_job(job_request, user_id)

@router.get("/mine")
async def get_own_jobs(
    request: Request,
    page: Optional[int] = Query(None, ge=1),
    size: Optional[int] = Query(None, ge=1),
    title: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> JSONResponse:
    user_id = request.headers.get("x-user-id")
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})

    return await job_service.get_own_jobs(db, user_id, page, size, title)

@router.get("/{job_id}")
async def get_job_detail(job_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    return await job_service.get_job_detail(job_id, db)

@router.put("/{job_id}")
async def update_job(
        request: Request,
        job_id: int,
        job_request: JobUpdateRequest,
        db: Session = Depends(get_db)
) -> JSONResponse:
    user_id = request.headers.get("x-user-id")
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})
    return await job_service.update_job(db, job_id, job_request, user_id)


@router.delete("/{job_id}")
def delete_job(
        request: Request,
        job_id: int,
        db: Session = Depends(get_db)
):
    user_id = request.headers.get("x-user-id")
    if user_id is None:
        return JSONResponse(status_code=400, content={"error": "Missing x-user-id header"})

    try:
        user_id = int(user_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid x-user-id header"})

    return job_service.delete_job(db, job_id, user_id)

@router.get("/")
def get_jobs_by_user(
    db: Session = Depends(get_db),
    uid: Optional[int] = Query(None, description="조회할 유저 ID"),
    page: Optional[int] = Query(None, ge=1),
    size: Optional[int] = Query(None, ge=1),
) -> JSONResponse:
    return job_service.get_jobs_by_user(db, uid, page, size)