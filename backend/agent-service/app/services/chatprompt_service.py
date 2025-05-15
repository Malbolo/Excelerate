from typing import Dict, List, Any

from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)

from app.utils.redis_chatprompt import PromptStore, load_chat_template
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


def get_prompt(agent: str, template_name: str) -> Dict[str, Any]:
    key = f"{agent}:{template_name}"
    msgs = store.load(key)
    if msgs is None:
        raise HTTPException(404, "Prompt not found")
    return {"name": key, "messages": msgs}


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
    norm = name.replace(" ", "_")
    prompt = load_chat_template(norm)
    chain = prompt | llm
    result = chain.invoke(variables)
    return result.content