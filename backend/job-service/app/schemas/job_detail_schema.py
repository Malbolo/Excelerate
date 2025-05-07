from typing import List
from pydantic import BaseModel

class CommandSchema(BaseModel):
    content: str
    order: int

class JobDetailSchema(BaseModel):
    id: int
    type: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    commands: List[CommandSchema]
    code: str

class JobDetailResponse(BaseModel):
    result: str
    data: JobDetailSchema

def create_job_detail_schema(job):
    return JobDetailSchema(
        id=job.id,
        type=job.type,
        title=job.title,
        description=job.description,
        data_load_command=job.data_load_command,
        data_load_url=job.data_load_url,
        code=job.code,
        commands=[
            CommandSchema(content=cmd.content, order=cmd.order)
            for cmd in sorted(job.commands, key=lambda x: x.order)
        ]
    )
