from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.redis_client import redis_client
from app.utils.redis_chatprompt import PromptStore

router = APIRouter()
store  = PromptStore(redis_client)

class MessageItem(BaseModel):
    role: str
    text: str

class PromptSchema(BaseModel):
    name: str
    messages: list[MessageItem]

@router.get("/", response_model=list[str])
def list_prompts():
    return store.list_names()

@router.get("/{name}", response_model=PromptSchema)
def get_prompt(name: str):
    msgs = store.load(name)
    if msgs is None:
        raise HTTPException(404, "Prompt not found")
    return {"name": name, "messages": msgs}

@router.post("/", status_code=201)
def create_prompt(p: PromptSchema):
    if store.load(p.name):
        raise HTTPException(400, "이미 존재하는 이름입니다")
    store.save(p.name, [m.dict() for m in p.messages])
    return {"ok": True}

@router.put("/{name}")
def update_prompt(name: str, p: PromptSchema):
    if name != p.name:
        raise HTTPException(400, "이름 변경은 지원하지 않음")
    store.save(name, [m.dict() for m in p.messages])
    return {"ok": True}

@router.delete("/{name}", status_code=204)
def delete_prompt(name: str):
    store.delete(name)
