from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MessageItem(BaseModel):
    role: str
    text: str

class PromptSchema(BaseModel):
    name: str
    messages: list[MessageItem]

class FewShotPair(BaseModel):
    human: str
    ai: str

class MessagesSchema(BaseModel):
    system: str
    fewshot: Optional[List[FewShotPair]] = None
    human: str

class InvokeRequest(BaseModel):
    messages: MessagesSchema
    variables: Dict[str, Any]

class InvokeTemplateRequest(BaseModel):
    template_name: str
    variables: Dict[str, Any]
