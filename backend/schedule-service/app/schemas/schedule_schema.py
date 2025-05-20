# app/schemas/schedule_schema.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# 베이스 모델
class JobBase(BaseModel):
    id: str
    order: int

# 요청 모델
class ScheduleCreateRequest(BaseModel):
    title: str
    description: str
    jobs: List[JobBase]
    success_emails: List[str] = Field(default_factory=list)
    failure_emails: List[str] = Field(default_factory=list)
    start_date: datetime
    end_date: Optional[datetime] = None
    execution_time: str
    frequency: str  # "daily", "weekly", "monthly" 또는 cron 표현식

class ScheduleUpdateRequest(BaseModel):
    title: str
    description: str
    jobs: List[JobBase]
    success_emails: List[str] = Field(default_factory=list)
    failure_emails: List[str] = Field(default_factory=list)
    start_date: datetime
    end_date: Optional[datetime] = None
    execution_time: str
    frequency: str

# 응답 모델
class ScheduleCreateResponse(BaseModel):
    schedule_id: str
    created_at: datetime

class ScheduleUpdateResponse(BaseModel):
    schedule_id: str
    updated_at: datetime

# 상세 정보 모델
class JobDetail(BaseModel):
    id: str
    order: int
    title: str
    description: str
    commands: List[str] = Field(default_factory=list)

class FrequencyDisplay(BaseModel):
    type: str
    time: str

class RunInfo(BaseModel):
    run_id: Optional[str] = None
    status: Optional[str] = None
    end_time: Optional[str] = None
    scheduled_time: Optional[str] = None

class ScheduleDetail(BaseModel):
    schedule_id: str
    title: str
    description: str
    frequency: str
    frequency_cron: str
    frequency_display: str
    is_paused: bool
    created_at: str
    updated_at: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    execution_time: str
    success_emails: List[str]
    failure_emails: List[str]
    jobs: List[JobDetail]

class ScheduleListItem(BaseModel):
    schedule_id: str
    title: str
    description: str
    is_paused: bool
    owner: str
    frequency_display: Optional[FrequencyDisplay] = None
    jobs: List[Dict[str, Any]] = Field(default_factory=list)
    last_run: Optional[RunInfo] = None
    next_run: Optional[RunInfo] = None
    end_date: Optional[str] = None

class PaginatedScheduleListResponse(BaseModel):
    schedules: List[ScheduleListItem]
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool

class ToggleResponse(BaseModel):
    schedule_id: str
    is_paused: bool

class ExecuteResponse(BaseModel):
    schedule_id: str
    run_id: str
    status: str
    execution_date: str