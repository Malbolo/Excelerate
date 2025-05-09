from fastapi import Query
from typing import List, Optional
from pydantic import BaseModel

class JobDetailRequest:
    def __init__(
        self,
        mine: bool = Query(...),
        name: Optional[str] = Query(None),
        dep: Optional[str] = Query(None),
        type: Optional[str] = Query(None),
        page: Optional[int] = Query(None, ge=1),
        size: Optional[int] = Query(None, ge=1),
        title: Optional[str] = Query(None),
    ):
        self.mine = mine
        self.name = name
        self.dep = dep
        self.type = type
        self.page = page
        self.size = size
        self.title = title

class CommandSchema(BaseModel):
    content: str
    order: int

class JobDetailSchema(BaseModel):
    id: str
    type: str
    user_name: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    commands: List[CommandSchema]
    code: str
    created_at: str

class JobDetailResponse(BaseModel):
    result: str
    data: Optional[JobDetailSchema]

def create_job_detail_schema(job):
    return JobDetailSchema(
        id=str(job.id),
        type=job.type,
        user_name=job.user_name,
        title=job.title,
        description=job.description,
        data_load_command=job.data_load_command,
        data_load_url=job.data_load_url,
        code=job.code,
        commands=[
            CommandSchema(content=cmd.content, order=cmd.order)
            for cmd in sorted(job.commands, key=lambda x: x.order)
        ],
        created_at=str(job.created_at)
    )
