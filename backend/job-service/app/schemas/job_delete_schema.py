from pydantic import BaseModel

class JobDeleteResponse(BaseModel):
    result: str
    data: None
