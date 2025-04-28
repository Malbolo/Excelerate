from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str = None

class CommandRequest(BaseModel):
    command_list: List[str] = None