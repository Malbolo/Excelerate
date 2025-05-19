from typing import List, Optional

from pydantic import BaseModel


class SourceData(BaseModel):
    factory_name: Optional[str] = None
    system_name: Optional[str] = None
    metric: Optional[str] = None
    factory_id: Optional[str] = None
    product_code: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class JobCreateRequest(BaseModel):
    type: str
    title: str
    description: str
    data_load_command: str
    data_load_url: str
    data_load_code: Optional[str] = None
    source_data: SourceData
    commands: List[str]
    code: str

class JobCreateResponseData(BaseModel):
    job_id: str
    created_at: str

class JobCreateResponse(BaseModel):
    result: str
    data : Optional[JobCreateResponseData]