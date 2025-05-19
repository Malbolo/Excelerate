import json
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from app.utils.redis_client import redis_client

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
    try:
        messages_data = prompt_store.load(name)["messages"]
        if messages_data is None:
            raise ValueError(f"Prompt '{name}' not found in Redis")

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
    except:
        return ChatPromptTemplate.from_messages([{"role": "system", "content": f"{name} 프롬프트가 없습니다."}])
