from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from langchain.callbacks.base import BaseCallbackHandler

from datetime import datetime
from zoneinfo import ZoneInfo
from langchain.callbacks.base import BaseCallbackHandler

class MemoryLogger(BaseCallbackHandler):
    def __init__(self):
        self.logs: list[dict] = []
        self.current_name: str | None = None
        self._last_prompts = None

    def set_name(self, name: str):
        """로깅할 때 사용할 이름을 지정합니다."""
        self.current_name = name

    def reset(self):
        """기존 로그를 초기화합니다."""
        self.logs = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        # name context 와 prompts를 임시로 저장
        self._last_prompts = prompts

    def on_llm_end(self, response, **kwargs):
        now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        # 실제 응답 메시지
        gen = response.generations[0][0].message
        entry = {
            "name":      self.current_name or "<unknown>",
            "input":     self._last_prompts[-1],
            "output":    gen.content,
            "timestamp": now,
            "metadata":  gen.response_metadata or {},
        }
        self.logs.append(entry)
