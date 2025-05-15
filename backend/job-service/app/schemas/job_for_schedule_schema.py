from typing import List, Optional

from pydantic import BaseModel


class JobForScheduleRequest(BaseModel):
    job_ids: List[str]

class JobForSchedule(BaseModel):
    id: str
    title: str
    description: str
    data_load_code: Optional[str] = None
    data_load_url: str
    code: str

    @classmethod
    def create(cls, job):
        return JobForSchedule(
            id=str(job.id),
            title=job.title,
            description=job.description,
            data_load_code=job.data_load_code,
            data_load_url=job.data_load_url,
            code=job.code,
        )

class JobForScheduleResponse(BaseModel):
    jobs: List[JobForSchedule]

class Command(BaseModel):
    content: str
    order: int

class JobForScheduleWithCommands(BaseModel):
    id: str
    title: str
    description: str
    data_load_code: Optional[str] = None
    data_load_url: str
    code: str
    commands: List[Command]

    @classmethod
    def create(cls, job):
        return JobForScheduleWithCommands(
            id=str(job.id),
            title=job.title,
            description=job.description,
            data_load_code=job.data_load_code,
            data_load_url=job.data_load_url,
            code=job.code,
            commands=[
                Command(content=cmd.content, order=cmd.order) for cmd in job.commands
            ]
        )

class JobForScheduleWithCommandsResponse(BaseModel):
    jobs: List[JobForScheduleWithCommands]
