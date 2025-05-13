from typing import List, Optional
from pydantic import BaseModel

class JobCreateRequest(BaseModel):
    type: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    data_load_code: Optional[str]
    commands: List[str]
    code: str

class JobCreateResponseData(BaseModel):
    job_id: str
    created_at: str

class JobCreateResponse(BaseModel):
    result: str
    data : Optional[JobCreateResponseData]