import asyncio
import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.cache.redis_client import RedisClient
from app.common.monitoring.metrics import (
    set_active_users,
    set_total_users,
    set_total_curriculums,
    set_public_curriculums,
    set_private_curriculums,
)
from app.modules.user.infrastructure.db_model.user import UserModel
from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel

logger = logging.getLogger(__name__)


class MetricsService:
    """메트릭 수집 및 업데이트 서비스"""

    def __init__(
        self,
        session: AsyncSession,
        redis_client: RedisClient,
        update_interval: int = 30,  # 30초마다 업데이트
    ):
        self.session = session
        self.redis_client = redis_client
        self.update_interval = update_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """메트릭 수집 시작"""
        if self._running:
            logger.warning("MetricsService is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._update_loop())
        logger.info("MetricsService started")

    async def stop(self) -> None:
        """메트릭 수집 중지"""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("MetricsService stopped")

    async def _update_loop(self) -> None:
        """주기적 메트릭 업데이트"""
        while self._running:
            try:
                await self.update_all_metrics()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(self.update_interval)

    async def update_all_metrics(self) -> None:
        """모든 메트릭 업데이트"""
        try:
            # 전체 사용자 수
            total_users = await self._get_total_users()
            set_total_users(total_users)

            # 활성 사용자 수 (Redis 기반)
            active_users = await self._get_active_users()
            set_active_users(active_users)

            # 커리큘럼 메트릭
            total_curriculums = await self._get_total_curriculums()
            set_total_curriculums(total_curriculums)

            public_curriculums = await self._get_public_curriculums()
            set_public_curriculums(public_curriculums)

            private_curriculums = await self._get_private_curriculums()
            set_private_curriculums(private_curriculums)

            logger.debug(
                f"Metrics updated - Users: {total_users} (active: {active_users}), "
                + f"Curriculums: {total_curriculums} (public: {public_curriculums}, private: {private_curriculums})"
            )

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

    async def _get_total_users(self) -> int:
        """전체 사용자 수 조회"""
        query = select(func.count()).select_from(UserModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_active_users(self) -> int:
        """활성 사용자 수 조회 (최근 5분간 활동)"""
        try:
            # Redis에서 활성 사용자 키 개수 확인
            # 활성 사용자는 "active_user:{user_id}" 형태로 저장됨
            # TTL 300초 (5분)로 설정

            # Redis SCAN으로 패턴 매칭하여 키 개수 계산
            cursor = 0
            active_count = 0

            while True:
                # Redis scan 명령어 직접 사용
                if self.redis_client.redis:
                    cursor, keys = await self.redis_client.redis.scan(
                        cursor, match="active_user:*", count=100
                    )
                    active_count += len(keys)

                    if cursor == 0:
                        break
                else:
                    break

            return active_count

        except Exception as e:
            logger.error(f"Failed to get active users count: {e}")
            return 0

    async def mark_user_active(self, user_id: str) -> None:
        """사용자를 활성 상태로 표시"""
        try:
            key = f"active_user:{user_id}"
            await self.redis_client.set(key, "1", ex=300)  # 5분 TTL
        except Exception as e:
            logger.error(f"Failed to mark user {user_id} as active: {e}")

    async def force_update(self) -> None:
        """즉시 메트릭 업데이트"""
        await self.update_all_metrics()

    async def _get_total_curriculums(self) -> int:
        """전체 커리큘럼 수 조회"""
        query = select(func.count()).select_from(CurriculumModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_public_curriculums(self) -> int:
        """공개 커리큘럼 수 조회"""
        query = (
            select(func.count())
            .select_from(CurriculumModel)
            .where(CurriculumModel.visibility == "PUBLIC")
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_private_curriculums(self) -> int:
        """비공개 커리큘럼 수 조회"""
        query = (
            select(func.count())
            .select_from(CurriculumModel)
            .where(CurriculumModel.visibility == "PRIVATE")
        )
        result = await self.session.execute(query)
        return result.scalar_one()
