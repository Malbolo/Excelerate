# memory_logger.py
import re, json

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

    @staticmethod
    def _parse_role_messages(text: str) -> List[dict]:
        """
        "System: ...\nHuman: ...\nAI: ..." 형태의 스트링을
        [{"role":"system","message":...}, ...] 로 분할 반환
        """
        pattern = re.compile(
            r'(System|Human|AI):\s*'          # Role
            r'(.*?)'                          # Message (non-greedy)
            r'(?=(?:System|Human|AI):|$)',    # Lookahead for next role or end
            re.DOTALL
        )
        out = []
        for m in pattern.finditer(text):
            role = m.group(1).lower()
            msg  = m.group(2).strip()
            out.append({"role": role, "message": msg})
        return out

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
        # raw prompt 문자열 가져와 role별 메시지 리스트로 파싱
        raw = self._last_prompts[-1] if self._last_prompts else ""
        parsed = self._parse_role_messages(raw)
        entry = LogDetail(
            name=self.current_name or "<unknown>",
            input=parsed, # list[dict] 형태로
            output=[{"role":"ai", "message": gen.content}],  # list[dict]
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
