from pydantic import BaseModel

class JobListResponse(BaseModel):
    result: str
    data: dict
