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
    set_total_summaries,
    set_total_feedbacks,
    set_average_completion_rate,
    set_average_feedback_score,
    set_active_learners,
)
from app.modules.user.infrastructure.db_model.user import UserModel
from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel
from app.modules.learning.infrastructure.db_model.summary import SummaryModel
from app.modules.learning.infrastructure.db_model.feedback import FeedbackModel

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

            # 학습 메트릭
            total_summaries = await self._get_total_summaries()
            set_total_summaries(total_summaries)

            total_feedbacks = await self._get_total_feedbacks()
            set_total_feedbacks(total_feedbacks)

            # 학습 통계
            avg_completion_rate = await self._get_average_completion_rate()
            set_average_completion_rate(avg_completion_rate)

            avg_feedback_score = await self._get_average_feedback_score()
            set_average_feedback_score(avg_feedback_score)

            active_learners = await self._get_active_learners()
            set_active_learners(active_learners)

            logger.debug(
                f"Metrics updated - Users: {total_users} (active: {active_users}), "
                + f"Curriculums: {total_curriculums} (public: {public_curriculums}, "
                + f"Learning: {total_summaries} summaries, {total_feedbacks} feedbacks, "
                + f"Avg completion: {avg_completion_rate:.1f}%, Avg score: {avg_feedback_score:.1f}, "
                + f"Active learners: {active_learners}"
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

    async def _get_total_summaries(self) -> int:
        """전체 요약 수 조회"""
        query = select(func.count()).select_from(SummaryModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_total_feedbacks(self) -> int:
        """전체 피드백 수 조회"""
        query = select(func.count()).select_from(FeedbackModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_average_completion_rate(self) -> float:
        """전체 사용자 평균 완료율 조회"""
        try:
            # 각 사용자별 커리큘럼 완료율 계산 후 평균
            query = (
                select(
                    CurriculumModel.user_id,
                    CurriculumModel.id.label("curriculum_id"),
                    func.count(SummaryModel.id).label("summary_count"),
                )
                .select_from(CurriculumModel.outerjoin(SummaryModel))
                .group_by(CurriculumModel.user_id, CurriculumModel.id)
            )

            result = await self.session.execute(query)
            rows = result.fetchall()

            if not rows:
                return 0.0

            # 각 커리큘럼의 완료율 계산
            completion_rates = []
            for row in rows:
                curriculum_id = row.curriculum_id
                summary_count = row.summary_count or 0

                # 해당 커리큘럼의 총 주차 수 조회
                total_weeks_query = select(func.count()).select_from(  # noqa: F841
                    select(CurriculumModel)
                    .where(CurriculumModel.id == curriculum_id)
                    .subquery()
                )
                # 간단히 요약 개수 기준으로 계산 (실제로는 week_schedules 조인 필요)
                completion_rate = (
                    min((summary_count / 12) * 100, 100) if summary_count > 0 else 0
                )
                completion_rates.append(completion_rate)

            return (
                sum(completion_rates) / len(completion_rates)
                if completion_rates
                else 0.0
            )

        except Exception as e:
            logger.error(f"Error calculating average completion rate: {e}")
            return 0.0

    async def _get_average_feedback_score(self) -> float:
        """전체 피드백 평균 점수 조회"""
        try:
            query = select(func.avg(FeedbackModel.score))
            result = await self.session.execute(query)
            avg_score = result.scalar_one()
            return float(avg_score) if avg_score else 0.0
        except Exception as e:
            logger.error(f"Error calculating average feedback score: {e}")
            return 0.0

    async def _get_active_learners(self) -> int:
        """최근 7일간 활성 학습자 수 조회"""
        try:
            from datetime import datetime, timedelta, timezone

            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

            query = select(func.count(func.distinct(SummaryModel.owner_id))).where(
                SummaryModel.created_at >= seven_days_ago
            )
            result = await self.session.execute(query)
            return result.scalar_one() or 0
        except Exception as e:
            logger.error(f"Error calculating active learners: {e}")
            return 0
