from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# 프롬프트 템플릿 저장용 모델
class MessageItem(BaseModel):
    role: str
    text: str

class PromptSchema(BaseModel):
    name: str
    messages: List[MessageItem]
    variables: Dict[str, Any]

# Client Request 용 모델
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
