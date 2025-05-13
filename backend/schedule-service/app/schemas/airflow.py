from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class DagCreate(BaseModel):
    """DAG 생성 요청 스키마"""
    name: str
    description: str
    cron_expression: str
    job_ids: List[str]
    owner: str
    start_date: datetime
    end_date: Optional[datetime] = None
    success_emails: Optional[List[str]] = None
    failure_emails: Optional[List[str]] = None
    execution_time: Optional[str] = None

class DagUpdate(BaseModel):
    """DAG 업데이트 요청 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None
    cron_expression: Optional[str] = None
    job_ids: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    success_emails: Optional[List[str]] = None
    failure_emails: Optional[List[str]] = None

class JobDetail(BaseModel):
    """Job 상세 정보 스키마"""
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    status: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None

class RunInfo(BaseModel):
    """실행 정보 스키마"""
    run_id: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    scheduled_time: Optional[str] = None

class FrequencyDisplay(BaseModel):
    """주기 표시 스키마"""
    type: str
    time: Optional[str] = None
    dayOfWeek: Optional[str] = None
    dayOfMonth: Optional[int] = None
    cronExpression: Optional[str] = None

class ScheduleDetail(BaseModel):
    """스케줄 상세 정보 스키마"""
    schedule_id: str
    title: str
    description: Optional[str] = None
    frequency: Optional[str] = None
    frequency_cron: Optional[str] = None
    frequency_display: Optional[FrequencyDisplay] = None
    is_paused: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    execution_time: Optional[str] = None
    success_emails: Optional[List[str]] = None
    failure_emails: Optional[List[str]] = None
    jobs: List[JobDetail]
    last_run: Optional[RunInfo] = None
    next_run: Optional[RunInfo] = None

class ScheduleList(BaseModel):
    """스케줄 목록 항목 스키마"""
    schedule_id: str
    title: str
    description: Optional[str] = None
    frequency: Optional[str] = None
    is_paused: bool
    jobs: List[JobDetail]
    last_run: Optional[RunInfo] = None
    next_run: Optional[RunInfo] = None

class ErrorLog(BaseModel):
    """에러 로그 스키마"""
    error_message: str
    error_trace: str
    error_time: Optional[str] = None
    error_code: Optional[str] = None

class TaskDetail(BaseModel):
    """태스크 상세 정보 스키마"""
    id: str
    title: str
    description: Optional[str] = None
    commands: Optional[List[Dict[str, Any]]] = None
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    logs_url: Optional[str] = None
    error_log: Optional[ErrorLog] = None

class RunSummary(BaseModel):
    """실행 요약 스키마"""
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    pending_jobs: int

class ScheduleRunDetail(BaseModel):
    """스케줄 실행 상세 정보 스키마"""
    schedule_id: str
    title: str
    description: Optional[str] = None
    run_id: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    jobs: List[TaskDetail]
    summary: RunSummary

class DagCalendarItem(BaseModel):
    """DAG 캘린더 항목 스키마"""
    date: str
    total: int
    success: int
    failed: int
    pending: int