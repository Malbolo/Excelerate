import json

class PromptStore:
    def __init__(self, client):
        self.redis = client

    def save(self, name: str, messages: list[dict]):
        key = f"prompts:{name}"
        payload = json.dumps({"messages": messages})
        # TTL 없이 영구 저장
        self.redis.set(key, payload)

    def load(self, name: str) -> list[dict] | None:
        key = f"prompts:{name}"
        data = self.redis.get(key)
        if not data:
            return None
        return json.loads(data)["messages"]

    def delete(self, name: str):
        self.redis.delete(f"prompts:{name}")

    def list_names(self) -> list[str]:
        return [k.split(":",1)[1] for k in self.redis.keys("prompts:*")]
