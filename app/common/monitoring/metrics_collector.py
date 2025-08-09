import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional

from sqlalchemy import Engine, QueuePool, func, select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection, AsyncEngine

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
    set_total_tags,
    set_total_categories,
    set_active_categories,
    set_total_curriculum_tags,
    set_total_curriculum_categories,
    set_popular_tags,
    set_average_tags_per_curriculum,
    set_total_likes,
    set_likes_per_curriculum,
    set_total_bookmarks,
    set_bookmarks_per_user,
    set_total_comments,
    set_comments_per_curriculum,
    set_total_follows,
    set_followers_per_user,
    set_active_social_users,
    set_social_engagement_rate,
    set_db_connection_metrics,
    set_cache_hit_ratio,
)
from app.modules.user.infrastructure.db_model.user import UserModel
from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel
from app.modules.learning.infrastructure.db_model.summary import SummaryModel
from app.modules.learning.infrastructure.db_model.feedback import FeedbackModel
from app.modules.taxonomy.infrastructure.db_model.tag import TagModel
from app.modules.taxonomy.infrastructure.db_model.category import CategoryModel
from app.modules.taxonomy.infrastructure.db_model.curriculum_tag import (
    CurriculumTagModel,
    CurriculumCategoryModel,
)
from app.modules.social.infrastructure.db_model.like import LikeModel
from app.modules.social.infrastructure.db_model.bookmark import BookmarkModel
from app.modules.social.infrastructure.db_model.comment import CommentModel
from app.modules.social.infrastructure.db_model.follow import FollowModel

logger = logging.getLogger(__name__)


class MetricsService:
    """메트릭 수집 및 업데이트 서비스"""

    def __init__(
        self,
        session: AsyncSession,
        redis_client: RedisClient,
        update_interval: int = 45,  # 45초마다 업데이트
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

            # 태그/카테고리 메트릭
            total_tags = await self._get_total_tags()
            set_total_tags(total_tags)

            total_categories = await self._get_total_categories()
            set_total_categories(total_categories)

            active_categories = await self._get_active_categories()
            set_active_categories(active_categories)

            total_curriculum_tags = await self._get_total_curriculum_tags()
            set_total_curriculum_tags(total_curriculum_tags)

            total_curriculum_categories = await self._get_total_curriculum_categories()
            set_total_curriculum_categories(total_curriculum_categories)

            popular_tags = await self._get_popular_tags()
            set_popular_tags(popular_tags)

            avg_tags_per_curriculum = await self._get_average_tags_per_curriculum()
            set_average_tags_per_curriculum(avg_tags_per_curriculum)

            total_likes = await self._get_total_likes()
            set_total_likes(total_likes)

            likes_per_curriculum = await self._get_likes_per_curriculum()
            set_likes_per_curriculum(likes_per_curriculum)

            # Bookmark 메트릭
            total_bookmarks = await self._get_total_bookmarks()
            set_total_bookmarks(total_bookmarks)

            bookmarks_per_user = await self._get_bookmarks_per_user()
            set_bookmarks_per_user(bookmarks_per_user)

            # Comment 메트릭
            total_comments = await self._get_total_comments()
            set_total_comments(total_comments)

            comments_per_curriculum = await self._get_comments_per_curriculum()
            set_comments_per_curriculum(comments_per_curriculum)

            # Follow 메트릭
            total_follows = await self._get_total_follows()
            set_total_follows(total_follows)

            followers_per_user = await self._get_followers_per_user()
            set_followers_per_user(followers_per_user)

            # Social Engagement 메트릭
            active_social_users = await self._get_active_social_users()
            set_active_social_users(active_social_users)

            engagement_rate = await self._get_social_engagement_rate(
                total_users, active_social_users
            )
            set_social_engagement_rate(engagement_rate)

            # DB 연결 풀 메트릭
            await self._update_db_connection_metrics()

            # Redis 캐시 메트릭
            await self._update_cache_metrics()

            logger.debug(
                f"Metrics updated - Users: {total_users} (active: {active_users}), "
                + f"Curriculums: {total_curriculums} (public: {public_curriculums} "
                + f"Learning: {total_summaries} summaries, {total_feedbacks} feedbacks, "
                + f"Avg completion: {avg_completion_rate:.1f}%, Avg score: {avg_feedback_score:.1f}, "
                + f"Taxonomy: {total_tags} tags, {total_categories} categories ({active_categories} active), "
                + f"Connections: {total_curriculum_tags} tag-assignments, {total_curriculum_categories} category-assignments"
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
                total_weeks_query = select(func.count()).select_from(
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

    async def _get_total_tags(self) -> int:
        """전체 태그 수 조회"""
        query = select(func.count()).select_from(TagModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_total_categories(self) -> int:
        """전체 카테고리 수 조회"""
        query = select(func.count()).select_from(CategoryModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_active_categories(self) -> int:
        """활성 카테고리 수 조회"""
        query = (
            select(func.count())
            .select_from(CategoryModel)
            .where(CategoryModel.is_active)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_total_curriculum_tags(self) -> int:
        """전체 커리큘럼-태그 연결 수 조회"""
        query = select(func.count()).select_from(CurriculumTagModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_total_curriculum_categories(self) -> int:
        """전체 커리큘럼-카테고리 연결 수 조회"""
        query = select(func.count()).select_from(CurriculumCategoryModel)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _get_popular_tags(self) -> int:
        """인기 태그 수 조회 (usage_count >= 10)"""
        try:
            query = (
                select(func.count())
                .select_from(TagModel)
                .where(TagModel.usage_count >= 10)
            )
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Error calculating popular tags: {e}")
            return 0

    async def _get_average_tags_per_curriculum(self) -> float:
        """커리큘럼당 평균 태그 수 조회"""
        try:
            # 커리큘럼별 태그 수 계산
            query = (
                select(func.count(CurriculumTagModel.tag_id).label("tag_count"))
                .select_from(CurriculumModel.outerjoin(CurriculumTagModel))
                .group_by(CurriculumModel.id)
            )

            result = await self.session.execute(query)
            tag_counts = [row.tag_count for row in result.fetchall()]

            if not tag_counts:
                return 0.0

            return sum(tag_counts) / len(tag_counts)

        except Exception as e:
            logger.error(f"Error calculating average tags per curriculum: {e}")
            return 0.0

    async def _get_total_likes(self) -> int:
        """전체 좋아요 수 조회"""
        try:
            query = select(func.count()).select_from(LikeModel)
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Error getting total likes: {e}")
            return 0

    async def _get_likes_per_curriculum(self) -> float:
        """커리큘럼당 평균 좋아요 수 조회"""
        try:
            query = (
                select(func.count(LikeModel.id).label("like_count"))
                .select_from(CurriculumModel.outerjoin(LikeModel))
                .group_by(CurriculumModel.id)
            )
            result = await self.session.execute(query)
            like_counts = [row.like_count for row in result.fetchall()]

            if not like_counts:
                return 0.0

            return sum(like_counts) / len(like_counts)
        except Exception as e:
            logger.error(f"Error calculating likes per curriculum: {e}")
            return 0.0

    async def _get_total_bookmarks(self) -> int:
        """전체 북마크 수 조회"""
        try:
            query = select(func.count()).select_from(BookmarkModel)
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Error getting total bookmarks: {e}")
            return 0

    async def _get_bookmarks_per_user(self) -> float:
        """사용자당 평균 북마크 수 조회"""
        try:
            query = (
                select(func.count(BookmarkModel.id).label("bookmark_count"))
                .select_from(UserModel.outerjoin(BookmarkModel))
                .group_by(UserModel.id)
            )
            result = await self.session.execute(query)
            bookmark_counts = [row.bookmark_count for row in result.fetchall()]

            if not bookmark_counts:
                return 0.0

            return sum(bookmark_counts) / len(bookmark_counts)
        except Exception as e:
            logger.error(f"Error calculating bookmarks per user: {e}")
            return 0.0

    async def _get_total_comments(self) -> int:
        """전체 댓글 수 조회"""
        try:
            query = select(func.count()).select_from(CommentModel)
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Error getting total comments: {e}")
            return 0

    async def _get_comments_per_curriculum(self) -> float:
        """커리큘럼당 평균 댓글 수 조회"""
        try:
            query = (
                select(func.count(CommentModel.id).label("comment_count"))
                .select_from(CurriculumModel.outerjoin(CommentModel))
                .group_by(CurriculumModel.id)
            )
            result = await self.session.execute(query)
            comment_counts = [row.comment_count for row in result.fetchall()]

            if not comment_counts:
                return 0.0

            return sum(comment_counts) / len(comment_counts)
        except Exception as e:
            logger.error(f"Error calculating comments per curriculum: {e}")
            return 0.0

    async def _get_total_follows(self) -> int:
        """전체 팔로우 관계 수 조회"""
        try:
            query = select(func.count()).select_from(FollowModel)
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Error getting total follows: {e}")
            return 0

    async def _get_followers_per_user(self) -> float:
        """사용자당 평균 팔로워 수 조회"""
        try:
            query = (
                select(func.count(FollowModel.id).label("follower_count"))
                .select_from(
                    UserModel.outerjoin(
                        FollowModel, UserModel.id == FollowModel.followee_id
                    )
                )
                .group_by(UserModel.id)
            )
            result = await self.session.execute(query)
            follower_counts = [row.follower_count for row in result.fetchall()]

            if not follower_counts:
                return 0.0

            return sum(follower_counts) / len(follower_counts)
        except Exception as e:
            logger.error(f"Error calculating followers per user: {e}")
            return 0.0

    async def _get_active_social_users(self) -> int:
        """최근 7일간 소셜 활동을 한 사용자 수 조회"""
        try:
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

            # 최근 7일간 좋아요, 댓글, 북마크, 팔로우 중 하나라도 한 사용자들
            like_users = select(LikeModel.user_id).where(
                LikeModel.created_at >= seven_days_ago
            )
            comment_users = select(CommentModel.user_id).where(
                CommentModel.created_at >= seven_days_ago
            )
            bookmark_users = select(BookmarkModel.user_id).where(
                BookmarkModel.created_at >= seven_days_ago
            )
            follow_users = select(FollowModel.follower_id).where(
                FollowModel.created_at >= seven_days_ago
            )

            # UNION으로 합치고 DISTINCT로 중복 제거
            active_users_query = like_users.union(
                comment_users, bookmark_users, follow_users
            )
            distinct_users_query = select(
                func.count(func.distinct(active_users_query.c.user_id))
            )

            result = await self.session.execute(distinct_users_query)
            return result.scalar_one() or 0

        except Exception as e:
            logger.error(f"Error calculating active social users: {e}")
            return 0

    async def _get_social_engagement_rate(
        self, total_users: int, active_social_users: int
    ) -> float:
        """소셜 참여율 계산"""
        if total_users == 0:
            return 0.0
        return (active_social_users / total_users) * 100

    # ========================= SYSTEM METRICS 메서드들 =========================

    async def _update_db_connection_metrics(self) -> None:
        """DB 연결 풀 메트릭 업데이트"""
        try:
            bind = self.session.get_bind()

            # 1) bind → sync_engine (초기값 보장)
            sync_engine: Optional[Engine] = None
            if isinstance(bind, AsyncConnection):
                sync_engine = bind.sync_engine
            elif isinstance(bind, AsyncEngine):
                sync_engine = bind.sync_engine

            if sync_engine is None:
                logger.debug("No sync_engine from bind: %s", type(bind).__name__)
                return

            # 2) 풀 조회
            pool = sync_engine.pool

            # 3) QueuePool일 때만 상세 지표
            pool_size = checked_out = overflow = 0
            if isinstance(pool, QueuePool):
                pool_size = int(pool.size())
                checked_out = int(pool.checkedout())
                overflow = int(pool.overflow())
            else:
                # NullPool 등은 수치 0 보고, 상태만 로그
                status = pool.status() if hasattr(pool, "status") else "<no status>"
                logger.debug(
                    "Non-QueuePool detected: %s | %s", type(pool).__name__, status
                )

            set_db_connection_metrics(pool_size, checked_out, overflow)

            # SQLAlchemy 연결 풀 정보 가져오기

            # pool = self.session.get_bind().pool

            # pool_size = pool.size()
            # checked_out = pool.checkedout()
            # overflow = pool.overflow()

            # set_db_connection_metrics(pool_size, checked_out, overflow)

        except Exception as e:
            logger.error(f"Error updating DB connection metrics: {e}")

    async def _update_cache_metrics(self) -> None:
        """캐시 메트릭 업데이트"""
        try:
            if not self.redis_client.redis:
                return

            # Redis 정보 가져오기
            info = await self.redis_client.redis.info()

            # 캐시 적중률 계산 (keyspace_hits / (keyspace_hits + keyspace_misses))
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)

            if hits + misses > 0:
                hit_ratio = (hits / (hits + misses)) * 100
                set_cache_hit_ratio(hit_ratio)
            else:
                set_cache_hit_ratio(0.0)

        except Exception as e:
            logger.error(f"Error updating cache metrics: {e}")
