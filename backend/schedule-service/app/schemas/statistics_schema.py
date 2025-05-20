# app/schemas/statistics_schema.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DailyStatItem(BaseModel):
    schedule_id: str
    run_id: Optional[str] = None
    title: str
    description: str
    owner: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    next_run_time: Optional[str] = None

class DailyStatisticsResponse(BaseModel):
    date: str
    success: List[DailyStatItem]
    failed: List[DailyStatItem]
    pending: List[DailyStatItem]

class MonthlyCalendarData(BaseModel):
    days: Dict[str, Dict[str, Any]]
    summary: Dict[str, int]
    monthly_total: Dict[str, int]

class MonthlyStatisticsResponse(BaseModel):
    data: MonthlyCalendarData