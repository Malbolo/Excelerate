from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class JobRequest(BaseModel):
    id: str
    order: int

class ScheduleCreateRequest(BaseModel):
    title: str
    description: str
    jobs: List[JobRequest]
    success_emails: List[str] = Field(default_factory=list)
    failure_emails: List[str] = Field(default_factory=list)
    start_date: datetime
    end_date: Optional[datetime] = None
    execution_time: datetime
    frequency: str  # "daily", "weekly", "monthly" 또는 cron 표현식

class ScheduleUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    jobs: Optional[List[JobRequest]] = None
    success_emails: Optional[List[str]] = None
    failure_emails: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    execution_time: Optional[datetime] = None
    frequency: Optional[str] = None