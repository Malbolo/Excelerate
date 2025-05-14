from typing import List, Optional
from pydantic import BaseModel

class JobForScheduleRequest(BaseModel):
    job_ids: List[str]

class JobListForSchedule(BaseModel):
    id: str
    title: str
    description: str
    data_load_code: Optional[str] = None
    data_load_url: str
    code: str

class JobForScheduleResponse(BaseModel):
    jobs: List[JobListForSchedule]

class Command(BaseModel):
    content: str
    order: int

class JobListForScheduleWithCommands(BaseModel):
    id: str
    title: str
    description: str
    data_load_code: Optional[str] = None
    data_load_url: str
    code: str
    commands: List[Command]

class JobForScheduleWithCommandsResponse(BaseModel):
    jobs: List[JobListForScheduleWithCommands]
