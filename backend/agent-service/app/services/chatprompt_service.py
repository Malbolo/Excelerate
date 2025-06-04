from typing import Dict, List, Any

from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)

from app.utils.chatprompt.redis_chatprompt import PromptStore, load_chat_template
from app.utils.redis_client import redis_client

# Redis 기반 스토어 인스턴스
store = PromptStore(redis_client)
# LangChain LLM 인스턴스
llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)


def list_grouped_prompts() -> Dict[str, List[str]]:
    names = store.list_names()
    grouped: Dict[str, List[str]] = {}
    for full_name in names:
        agent, template = full_name.split(":", 1)
        grouped.setdefault(agent, []).append(template)
    return grouped


def get_prompt_json(agent: str, template_name: str) -> Dict[str, Any]:
    key = f"{agent}:{template_name}"

    data = store.load(key)
    if data is None:
        # Redis에 프롬프트가 없으면 ChatPromptTemplate 폴백
        prompt = load_chat_template(key)

        # ChatPromptTemplate 내부 메시지 리스트 꺼내기
        raw_msgs: List[Dict[str,str]] = []
        for m in getattr(prompt, "prompt_messages", getattr(prompt, "messages", [])):
            if isinstance(m, SystemMessagePromptTemplate):
                role = "system"
            elif isinstance(m, HumanMessagePromptTemplate):
                role = "human"
            elif isinstance(m, AIMessagePromptTemplate):
                role = "ai"
            else:
                continue
            
            text = getattr(m, "template", None) or m.prompt.template
            raw_msgs.append({"role": role, "text": text})

        msgs = raw_msgs
        variables = {var: "" for var in prompt.input_variables}
    else:
        # 원래 로직 유지
        msgs      = data.get("messages", [])
        variables = data.get("variables", {})

    if msgs is None:
        raise HTTPException(404, "Prompt not found")
    if len(msgs) < 2:
        raise HTTPException(500, "Invalid prompt format: insufficient messages")
    # 첫 system 메시지
    system_text = msgs[0]["text"]
    # 마지막 human 메시지
    human_text = msgs[-1]["text"]
    # 중간 fewshot 쌍 생성
    fewshot: List[Dict[str, str]] = []
    for i in range(1, len(msgs) - 1, 2):
        role_h = msgs[i]["role"].lower()
        role_a = msgs[i+1]["role"].lower() if i+1 < len(msgs) else None
        if role_h == "human" and role_a == "ai":
            fewshot.append({"human": msgs[i]["text"], "ai": msgs[i+1]["text"]})
    return {"template_name": template_name ,"system": system_text, "fewshot": fewshot, "human": human_text, "variables": variables}


def invoke_with_messages(messages: List[Dict[str, str]], variables: Dict[str, Any]) -> str:
    templates = []
    for m in messages:
        role = m["role"].lower()
        text = m["text"]
        if role == "system":
            templates.append(SystemMessagePromptTemplate.from_template(text))
        elif role == "human":
            templates.append(HumanMessagePromptTemplate.from_template(text))
        elif role == "ai":
            templates.append(AIMessagePromptTemplate.from_template(text))
        else:
            raise HTTPException(400, f"Unsupported role: {m['role']}")
    prompt = ChatPromptTemplate.from_messages(templates)
    chain = prompt | llm
    result = chain.invoke(variables)
    return result.content


def invoke_with_template(name: str, variables: Dict[str, Any]) -> str:
    prompt = load_chat_template(name)
    chain = prompt | llm
    result = chain.invoke(variables)
    return result.content