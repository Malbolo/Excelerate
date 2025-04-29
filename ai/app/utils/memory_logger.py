from datetime import datetime
from typing import List
from langchain.callbacks.base import BaseCallbackHandler

class MemoryLogger(BaseCallbackHandler):
    def __init__(self):
        self.logs: List[dict] = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        # model_name이 없으면 name 키를, 그래도 없으면 "<unknown>"을 사용
        model = serialized.get("model_name") \
                or serialized.get("name") \
                or "<unknown>"
        self.logs.append({
            "event": "llm_start",
            "model": model,
            "prompts": prompts,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def on_llm_end(self, response, **kwargs):
        self.logs.append({
            "event": "llm_end",
            "token_usage": response.llm_output.get("token_usage", {}),
            "timestamp": datetime.utcnow().isoformat(),
        })

    def on_chain_start(self, serialized, inputs, **kwargs):
        self.logs.append({
            "event": "chain_start",
            "chain": serialized["name"],
            "inputs": inputs,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def on_chain_end(self, outputs, **kwargs):
        self.logs.append({
            "event": "chain_end",
            "outputs": outputs,
            "timestamp": datetime.utcnow().isoformat(),
        })

    # 필요에 따라 on_tool_start, on_tool_end, on_error 등 추가
    def reset(self):
        self.logs = []
