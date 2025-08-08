import json
from typing import Dict, List, Optional, Union
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Redis 연결"""
        self.redis = redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )

    async def disconnect(self):
        """Redis 연결 해제"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        """키로 값 조회"""
        if not self.redis:
            return None
        return await self.redis.get(key)

    async def set(
        self, key: str, value: Union[str, Dict, List], ex: Optional[int] = None
    ) -> bool:
        """키-값 저장"""
        if not self.redis:
            return False

        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)

        return await self.redis.set(key, value, ex=ex)

    async def delete(self, key: str) -> int:
        """키 삭제"""
        if not self.redis:
            return 0
        return await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        if not self.redis:
            return False
        return bool(await self.redis.exists(key))

    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Sorted Set에 값 추가"""
        if not self.redis:
            return 0
        return await self.redis.zadd(key, mapping)

    async def zrevrange(
        self, key: str, start: int, end: int, withscores: bool = False
    ) -> List[Union[str, tuple]]:
        """Sorted Set에서 역순으로 범위 조회"""
        if not self.redis:
            return []
        return await self.redis.zrevrange(key, start, end, withscores=withscores)

    async def zrem(self, key: str, *members) -> int:
        """Sorted Set에서 멤버 제거"""
        if not self.redis:
            return 0
        return await self.redis.zrem(key, *members)

    async def expire(self, key: str, seconds: int) -> bool:
        """키 만료 시간 설정"""
        if not self.redis:
            return False
        return await self.redis.expire(key, seconds)


# 싱글톤 인스턴스
redis_client = RedisClient()
