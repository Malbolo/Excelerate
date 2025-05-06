from typing import List, Optional
from pydantic import BaseModel

class ScheduleListItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str

class DailySchedulesResponse(BaseModel):
    result: str
    data: Optional[dict] = None