from pydantic import BaseModel

class JobDeleteSchema(BaseModel):
    result: str
    data: None