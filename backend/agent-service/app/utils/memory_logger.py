# memory_logger.py

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional

from langchain.callbacks.base import BaseCallbackHandler
from app.models.log import LogDetail

class MemoryLogger(BaseCallbackHandler):
    def __init__(self):
        self.logs: List[LogDetail] = []
        self.current_name: Optional[str] = None
        self._last_prompts: Optional[List[str]] = None

    def set_name(self, name: str):
        """로깅할 때 사용할 이름을 지정합니다."""
        self.current_name = name

    def reset(self):
        """기존 로그를 초기화합니다."""
        self.logs = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        """LLM 호출 전 입력 프롬프트 저장"""
        self._last_prompts = prompts

    def on_llm_end(self, response, **kwargs):
        """LLM 응답 후 로그 저장"""
        now = datetime.now(ZoneInfo("Asia/Seoul"))

        gen = response.generations[0][0].message
        entry = LogDetail(
            name=self.current_name or "<unknown>",
            input=self._last_prompts[-1] if self._last_prompts else "",
            output=gen.content,
            timestamp=now,
            metadata=gen.response_metadata or {}
        )
        self.logs.append(entry)

    def get_logs(self) -> List[LogDetail]:
        """LogDetail 객체 리스트 반환"""
        return self.logs

    def get_serialized_logs(self) -> List[dict]:
        """JSON 직렬화된 로그 리스트 반환 (datetime 포함)"""
        return [log.model_dump() for log in self.logs]
