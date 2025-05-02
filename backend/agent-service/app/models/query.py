from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str = None

class CommandRequest(BaseModel):
    command_list: List[str] = None
    url: str = None

class DataRequest(BaseModel):
    command: str = None

class RagRequest(BaseModel):
    data: List[dict] = None