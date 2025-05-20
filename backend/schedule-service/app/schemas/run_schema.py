# app/schemas/run_schema.py
from typing import List, Optional
from pydantic import BaseModel, Field

class ErrorLog(BaseModel):
    error_message: str
    error_trace: Optional[str] = None
    error_time: Optional[str] = None
    error_code: Optional[str] = None

class RunDetail(BaseModel):
    run_id: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None

class JobRunDetail(BaseModel):
    id: str
    title: str
    description: str
    commands: List[str] = Field(default_factory=list)
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    logs_url: str
    error_log: Optional[ErrorLog] = None

class RunSummary(BaseModel):
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    pending_jobs: int

class ScheduleRunDetailResponse(BaseModel):
    schedule_id: str
    title: str
    description: str
    run_id: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    jobs: List[JobRunDetail]
    summary: RunSummary

class ScheduleRunsResponse(BaseModel):
    schedule_id: str
    title: str
    runs: List[RunDetail]
    page: int
    size: int
    total: int