from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class JobCommandDetail(BaseModel):
    content: str
    status: str
    order: int

class JobDetail(BaseModel):
    id: int
    name: str
    order: int
    commands: List[JobCommandDetail]

class ScheduleDetailResponse(BaseModel):
    result: str
    data: Optional[dict] = None