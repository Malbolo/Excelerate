from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str = None

class CommandRequest(BaseModel):
    command_list: List[str] = None
    url: str = None
    uid: Optional[str] = None
    stream_id: Optional[str] = None

class DataRequest(BaseModel):
    command: str = None,
    stream_id: Optional[str] = None

class RagRequest(BaseModel):
    data: List[dict] = None