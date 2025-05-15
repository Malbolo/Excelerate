from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any

from app.models.chatprompt import PromptSchema, InvokeRequest, InvokeTemplateRequest

from app.utils.docs import ChatDocs
from app.utils.redis_client import redis_client
from app.utils.redis_chatprompt import PromptStore

from app.services.chatprompt_service import (
    list_grouped_prompts,
    get_prompt,
    invoke_with_messages,
    invoke_with_template,
)

docs = ChatDocs()
router = APIRouter()
store  = PromptStore(redis_client)

llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)

@router.get("/", response_model=Dict[str, List[str]])
def list_prompts_grouped():
    """
    Agent별로 템플릿 이름 리스트를 그룹화하여 반환합니다.
    예시:
    {
      "Code_Generator": ["Manipulate_Excel", "AnotherTemplate"],
      "Data_Loader": ["LoadFromAPI"]
    }
    """
    data = list_grouped_prompts()
    return JSONResponse(status_code=200, content={"result": "success", "data": data})

@router.get("/{agent}/{template_name}", response_model=PromptSchema)
def get_prompt_by_agent_template(agent: str, template_name: str):
    """
    agent와 template_name을 받아 복합 키(f"{agent}:{template_name}")로 Redis에서 프롬프트를 조회합니다.
    """
    name = f"{agent}:{template_name}"
    msgs = store.load(name)
    if msgs is None:
        raise HTTPException(404, "Prompt not found")
    return JSONResponse(status_code=200, content={"result": "success", "data": {"name": name, "messages": msgs}})

@router.post("/invoke/messages", response_model=Any)
def invoke_messages(req: InvokeRequest = docs.invoke["split"]) -> JSONResponse:
    """
    사용자로부터 받은 messages 리스트와 variables로
    ChatPromptTemplate을 동적으로 생성하여 LLM을 호출합니다.

    - messages: [ {role, text}, ... ]
    - variables: {key: value, ...}
    플레이스홀더 {key}를 메시지 내에서 교체하지 않고,
    ChatPromptTemplate의 input_variables로 설정합니다.
    """
    try:
        content = invoke_with_messages([m.dict() for m in req.messages], req.variables)
    except HTTPException as e:
        raise e
    return JSONResponse(status_code=200, content={"result": "success", "data": content})

@router.post("/invoke/template", response_model=Any)
def invoke_template(req: InvokeTemplateRequest = docs.invoke["template"]) -> JSONResponse:
    """
    저장된 template_name에 variables를 넣어 LLM 호출 결과를 반환합니다.
    load_chat_template 함수를 사용하여 ChatPromptTemplate을 생성합니다.
    """
    try:
        content = invoke_with_template(req.template_name, req.variables)
    except HTTPException as e:
        raise e
    return JSONResponse(status_code=200, content={"result": "success", "data": content})

# 개발자 관리용 API -------------------------------
@router.get("/dev/fetch/list", response_model=list[str])
def list_prompts():
    return store.list_names()

@router.get("/{name}", response_model=PromptSchema)
def get_prompt(name: str):
    msgs = store.load(name)
    if msgs is None:
        raise HTTPException(404, "Prompt not found")
    return JSONResponse(status_code=200, content={"result" : "success", "data" : {"name": name, "messages": msgs}})

@router.post("/", status_code=201)
def create_prompt(p: PromptSchema):
    if store.load(p.name):
        raise HTTPException(400, "이미 존재하는 이름입니다")
    store.save(p.name, [m.dict() for m in p.messages])
    return JSONResponse(status_code=201, content={"result" : "success", "data" : f"{p.name} 템플릿이 등록되었습니다."})

@router.put("/{name}")
def update_prompt(name: str, p: PromptSchema):
    if name != p.name:
        raise HTTPException(400, "이름 변경은 지원하지 않음")
    store.save(name, [m.dict() for m in p.messages])
    return JSONResponse(status_code=200, content={"result" : "success", "data" : f"{name} 템플릿이 업데이트 되었습니다."})

@router.delete("/{name}", status_code=204)
def delete_prompt(name: str):
    store.delete(name)
    JSONResponse(status_code=204, content={"result" : "success", "data" : f"{name} 템플릿이 삭제되었습니다."})
