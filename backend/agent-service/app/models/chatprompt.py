from pydantic import BaseModel
from typing import List, Dict, Any

class MessageItem(BaseModel):
    role: str
    text: str

class PromptSchema(BaseModel):
    name: str
    messages: list[MessageItem]

class InvokeRequest(BaseModel):
    messages: List[MessageItem]
    variables: Dict[str, Any]

class InvokeTemplateRequest(BaseModel):
    template_name: str
    variables: Dict[str, Any]