from typing import List
from pydantic import BaseModel

class JobCreateRequest(BaseModel):
    type: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    commands: List[str]
    code: str

class JobCreateResponse(BaseModel):
    result: str
    data : dict