# memory_logger.py
import re

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
        self._start_time: Optional[datetime] = None

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
        self._start_time = datetime.now(ZoneInfo("UTC"))

    def on_llm_end(self, response, **kwargs):
        """LLM 응답 후, 로그를 생성하고 지연(latency)을 메타데이터에 추가합니다."""
        end_time = datetime.now(ZoneInfo("UTC"))
        # 시작 시간이 기록되어 있으면 지연 계산
        latency = None
        if self._start_time:
            latency = (end_time - self._start_time).total_seconds()

        # 응답 메시지
        gen = response.generations[0][0].message
        # 마지막 프롬프트 raw 문자열
        raw = self._last_prompts[-1] if self._last_prompts else ""
        parsed = self._parse_role_messages(raw)

        # 기본 메타데이터 가져오기
        metadata = gen.response_metadata or {}
        # 지연 정보와 타임스탬프 추가
        if latency is not None:
            metadata['llm_latency'] = latency  # seconds

        # 로그 엔트리 생성
        entry = LogDetail(
            name=self.current_name or "<unknown>",
            input=parsed,
            output=[{"role": "ai", "message": gen.content}],
            timestamp=end_time,
            metadata=metadata
        )
        self.logs.append(entry)

    def get_logs(self) -> List[LogDetail]:
        """LogDetail 객체 리스트 반환"""
        return self.logs

    def get_serialized_logs(self) -> List[dict]:
        """JSON 직렬화된 로그 리스트 반환 (datetime 포함)"""
        return [log.model_dump() for log in self.logs]
