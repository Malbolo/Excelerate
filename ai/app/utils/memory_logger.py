from datetime import datetime
from zoneinfo import ZoneInfo
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
            "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        })

    def on_llm_end(self, response, **kwargs):
        # print("on_llm_end", response.generations[0][0])
        self.logs.append({
            "event": "llm_end",
            "output" : response.generations[0][0].message.content,
            "metadata" : response.generations[0][0].message.response_metadata,
            "token_usage": response.llm_output.get("token_usage", {}),
            "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        })

    def on_chain_start(self, serialized, inputs, **kwargs):
        # print("se" + serialized)
        self.logs.append({
            "event": "chain_start",
            "chain": serialized["name"],
            "inputs": inputs,
            "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        })

    def on_chain_end(self, outputs, **kwargs):
        # print("op" + outputs)
        self.logs.append({
            "event": "chain_end",
            "outputs": outputs,
            "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        })

    # 필요에 따라 on_tool_start, on_tool_end, on_error 등 추가
    def reset(self):
        self.logs = []
