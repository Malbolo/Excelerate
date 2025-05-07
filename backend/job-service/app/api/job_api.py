from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.core import auth
from app.db.database import get_db
from app.schemas.job_create_schema import JobCreateRequest
from app.schemas.job_update_schema import JobUpdateRequest
from app.services import job_service

router = APIRouter(
    prefix="/api/jobs"
)

@router.post("")
async def create_job(request: Request, job_request: JobCreateRequest, db: Session = Depends(get_db)) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)
    return await job_service.create_job(job_request, user_id, db)

@router.get("")
def get_jobs(
        request: Request,
        db:Session = Depends(get_db),
        mine: bool = Query(...),
        name: Optional[str] = Query(None),
        dep: Optional[str] = Query(None),
        type: Optional[str] = Query(None),
        page: Optional[int] = Query(None, ge=1),
        size: Optional[int] = Query(None, ge=1),
        title: Optional[str] = Query(None)
) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)
    return job_service.get_jobs(db, mine, name, dep, type, page, size, title, user_id)

@router.get("/{job_id}")
async def get_job_detail(request: Request, job_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)
    return await job_service.get_job_detail(job_id, db)

@router.put("/{job_id}")
async def update_job(
        request: Request,
        job_id: int,
        job_request: JobUpdateRequest,
        db: Session = Depends(get_db)
) -> JSONResponse:
    user_id = auth.get_user_id_from_header(request)
    return await job_service.update_job(db, job_id, job_request, user_id)


@router.delete("/{job_id}")
def delete_job(
        request: Request,
        job_id: int,
        db: Session = Depends(get_db)
):
    user_id = auth.get_user_id_from_header(request)
    return job_service.delete_job(db, job_id, user_id)
