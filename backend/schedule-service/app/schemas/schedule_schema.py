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
    execution_time: str
    frequency: str  # "daily", "weekly", "monthly" 또는 cron 표현식

class ScheduleUpdateRequest(BaseModel):
    title: str
    description: str
    jobs: List[JobRequest]
    success_emails: List[str] = Field(default_factory=list)
    failure_emails: List[str] = Field(default_factory=list)
    start_date: datetime
    end_date: Optional[datetime] = None
    execution_time: str
    frequency: str  # "daily", "weekly", "monthly" 또는 cron 표현식