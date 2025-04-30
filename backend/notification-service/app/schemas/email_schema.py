from pydantic import BaseModel, EmailStr
from typing import List

class EmailSchema(BaseModel):
    email: List[EmailStr]
    subject: str
    message: str

# class EmailCRUD(BaseModel):
#     recipients: List[EmailStr]
#     subject: str
#     message: str
#     error: str