from typing import List
from pydantic import BaseModel

class CommandSchema(BaseModel):
    content: str
    order: int

class JobDetailResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    commands: List[CommandSchema]
    code: str
