from typing import List
from pydantic import BaseModel

class JobUpdateRequest(BaseModel):
    type: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    commands: List[str]
    code: str

class JobUpdateResponse(BaseModel):
    result: str
    data : dict