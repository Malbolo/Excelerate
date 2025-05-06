from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class JobReference(BaseModel):
    id: int
    order: int

class ScheduleCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    jobs: List[JobReference]
    success_emails: Optional[List[str]] = None
    failure_emails: Optional[List[str]] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    execution_time: datetime
    frequency: str  # daily, weekly, monthly, yearly, cron

class ScheduleCreateResponse(BaseModel):
    result: str
    data: Optional[dict] = None