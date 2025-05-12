from typing import List, Optional
from pydantic import BaseModel

class JobUpdateRequest(BaseModel):
    type: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    commands: List[str]
    code: str

class JobUpdateResponseData(BaseModel):
    job_id: str
    updated_at: str

class JobUpdateResponse(BaseModel):
    result: str
    data : Optional[JobUpdateResponseData]
