import json
import redis
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from app.utils import date_utils

class RedisCalendarCache:
    def __init__(self, redis_url: str, ttl_seconds: int = 86400):
        self.redis = redis.from_url(redis_url)
        self.ttl = ttl_seconds
        self.prefix = "calendar:"

    def _get_key(self, year: int, month: int) -> str:
        """Redis 키 생성"""
        return f"{self.prefix}{year}-{month:02d}"

    def get(self, year: int, month: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """캐시에서 월별 데이터 조회"""
        key = self._get_key(year, month)
        data = self.redis.get(key)

        if data:
            # JSON 문자열을 파이썬 객체로 변환
            return True, json.loads(data)

        return False, None

    def set(self, year: int, month: int, calendar_data: List[Dict[str, Any]]):
        """월별 데이터를 캐시에 저장 (업데이트 시간 포함)"""
        key = self._get_key(year, month)

        # 현재 시간을 ISO 형식으로 포함
        now = date_utils.get_now_utc().isoformat()

        # 데이터와 메타데이터를 함께 저장
        cache_data = {
            "calendar_data": calendar_data,
            "updated_at": now,
            "cache_generated": True
        }

        # 파이썬 객체를 JSON 문자열로 변환하여 저장
        json_data = json.dumps(cache_data)
        self.redis.setex(key, self.ttl, json_data)

    def invalidate(self, year: int, month: int):
        """특정 월의 캐시 무효화"""
        key = self._get_key(year, month)
        self.redis.delete(key)