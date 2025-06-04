import json
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from app.utils.redis_client import redis_client
from typing import Callable
from app.utils.chatprompt.chatprompt_default import (
    extract_datacall_params_prompt,
    transform_date_params_template,
    split_command_list_template,
    generate_code_template,
    generate_code_extension_template,
    manipulate_excel_template
)

# default 템플릿 매핑
DEFAULT_PROMPT_MAP: dict[str, Callable[[], ChatPromptTemplate]] = {
    "Data Loader:Extract DataCall Params": extract_datacall_params_prompt,
    "Data Loader:Transform Date Params": transform_date_params_template,
    "Code Generator:Split Command List": split_command_list_template,
    "Code Generator:Generate Code" : generate_code_template,
    "Code Generator:Generate Code Extension" : generate_code_extension_template,
    "Code Generator:Manipulate Excel": manipulate_excel_template,
}

class PromptStore:
    def __init__(self, client):
        self.redis = client

    def save(self, name: str, messages: list[dict], variables: dict):
        key = f"prompts:{name}"
        payload = json.dumps({"messages": messages, "variables": variables})
        # TTL 없이 영구 저장
        self.redis.set(key, payload)

    def load(self, name: str) -> dict | None:
        key = f"prompts:{name}"
        data = self.redis.get(key)
        if not data:
            return None
        return json.loads(data)

    def delete(self, name: str):
        self.redis.delete(f"prompts:{name}")

    def list_names(self) -> list[str]:
        return [k.split(":",1)[1] for k in self.redis.keys("prompts:*")]
    

prompt_store = PromptStore(redis_client)

def load_chat_template(name: str) -> ChatPromptTemplate:
    """
    Redis 에서 name 으로 불러온 메시지 리스트를
    LangChain 의 ChatPromptTemplate 으로 변환하여 반환합니다.
    role 은 반드시 'system', 'human', 'ai' 중 하나여야 합니다.
    """
    data = prompt_store.load(name)
    if data is None:
        # Redis에 없으면 기본 맵에서 꺼내 실행
        default_fn = DEFAULT_PROMPT_MAP.get(name)
        if default_fn:
            return default_fn()
        raise KeyError(f"Prompt '{name}' not found in Redis and no default registered")

    messages_data = data["messages"]
    prompt_messages = []
    for msg in messages_data:
        role = msg["role"]
        text = msg["text"]
        if role == "system":
            prompt_messages.append(
                SystemMessagePromptTemplate.from_template(text)
            )
        elif role == "human":
            prompt_messages.append(
                HumanMessagePromptTemplate.from_template(text)
            )
        elif role == "ai":
            prompt_messages.append(
                AIMessagePromptTemplate.from_template(text)
            )
        else:
            raise ValueError(f"Unknown role '{role}' in prompt '{name}'")

    return ChatPromptTemplate.from_messages(prompt_messages)
