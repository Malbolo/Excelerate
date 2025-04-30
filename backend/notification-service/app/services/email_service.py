from typing import List
from fastapi import UploadFile, File, Form
from fastapi_mail import MessageSchema, MessageType, FastMail
from pydantic import EmailStr
from starlette.responses import JSONResponse
from core import email_connection_config
from schemas.email_schema import EmailSchema

conf = email_connection_config.conf

async def handle_sending_email(email: EmailSchema) -> JSONResponse:
    email_data = MessageSchema(
        subject = email.subject,
        recipients = email.dict().get("email"),
        body = email.message,
        subtype = MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(email_data)
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})

    return JSONResponse(status_code=200, content={"message" : "email sent successfully"})

async def handle_sending_email_with_files(
    file: List[UploadFile] = File(...),
    email: EmailStr = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
) -> JSONResponse:
    email_data = MessageSchema(
        subject=subject,
        recipients=[email],
        body=message,
        subtype=MessageType.html,
        attachments=file
    )
    fm = FastMail(conf)

    try:
        await fm.send_message(email_data)
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})

    return JSONResponse(status_code=200, content={"message" : "email sent successfully"})
