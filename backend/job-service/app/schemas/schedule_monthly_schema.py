from typing import List, Optional
from pydantic import BaseModel

class DailyStatItem(BaseModel):
    day: int
    pending: int
    success: int
    fail: int

class MonthlyStatisticsResponse(BaseModel):
    result: str
    data: Optional[dict] = None