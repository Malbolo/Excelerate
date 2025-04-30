from typing import List
from fastapi import APIRouter, File, UploadFile, Form
from pydantic import EmailStr
from starlette.responses import JSONResponse
from app.schemas.email_schema import EmailSchema
from app.services.email_service import (
    handle_sending_email,
    handle_sending_email_with_files
)

router = APIRouter(
    prefix="/notification"
)

@router.post("/email")
async def send_email(email: EmailSchema) -> JSONResponse:
    return await handle_sending_email(email)

@router.post("/email/with-files")
async def send_file(
    file: List[UploadFile] = File(...),
    email: EmailStr = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
) -> JSONResponse:
    return await handle_sending_email_with_files(file, email, subject, message)
