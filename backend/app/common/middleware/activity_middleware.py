import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.common.cache.redis_client import redis_client
from app.core.auth import decode_access_token

logger = logging.getLogger(__name__)


class ActivityTrackingMiddleware(BaseHTTPMiddleware):
    """사용자 활동 추적 미들웨어"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # 요청 처리
        response = await call_next(request)

        # 인증된 사용자의 활동 추적
        await self._track_user_activity(request)

        return response

    async def _track_user_activity(self, request: Request) -> None:
        """사용자 활동 추적"""
        try:
            # Authorization 헤더에서 토큰 추출
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return

            token = auth_header.split(" ")[1]

            # 토큰 디코딩으로 사용자 ID 획득
            payload = decode_access_token(token)
            user_id = payload.get("sub")

            if user_id:
                # Redis에 활성 사용자 표시 (5분 TTL)
                key = f"active_user:{user_id}"
                await redis_client.set(key, "1", ex=300)

        except Exception as e:
            # 인증 실패는 정상적인 상황이므로 에러 로그 생략
            logger.debug(f"Activity tracking failed: {e}")
            pass
