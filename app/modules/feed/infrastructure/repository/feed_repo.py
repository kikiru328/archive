import json
from typing import List, Tuple, Optional
from sqlalchemy import Result, Select, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.common.cache.redis_client import redis_client
from app.modules.feed.domain.repository.feed_repo import IFeedRepository
from app.modules.feed.domain.entity.feed_item import FeedItem
from app.modules.feed.domain.vo.feed_filter import FeedFilter
from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel
from app.modules.user.infrastructure.db_model.user import UserModel
from app.modules.taxonomy.infrastructure.db_model.category import CategoryModel
from app.modules.taxonomy.infrastructure.db_model.curriculum_tag import (
    CurriculumCategoryModel,
    CurriculumTagModel,
)
from app.modules.taxonomy.infrastructure.db_model.tag import TagModel


class FeedRepository(IFeedRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.CACHE_KEY_PREFIX = "feed"
        self.CACHE_EXPIRE_TIME = 300  # 5분
        self.SORTED_SET_KEY = "feed:public_curriculums"

    async def get_public_feed(
        self, feed_filter: FeedFilter
    ) -> Tuple[int, List[FeedItem]]:
        """공개 커리큘럼 피드 조회 (캐시 우선, DB 백업)"""

        # 1. 캐시에서 시도
        cached_items = await self._get_from_cache(feed_filter)
        if cached_items is not None:
            return cached_items

        # 2. DB에서 조회
        total_count, feed_items = await self._get_from_database(feed_filter)

        # 3. 캐시에 저장
        await self._cache_feed_items(feed_items, feed_filter)

        return total_count, feed_items

    async def _get_from_cache(
        self, feed_filter: FeedFilter
    ) -> Optional[Tuple[int, List[FeedItem]]]:
        """캐시에서 피드 조회"""
        try:
            # Sorted Set에서 최신순으로 조회
            start = feed_filter.offset
            end = start + feed_filter.limit - 1

            curriculum_ids = await redis_client.zrevrange(
                self.SORTED_SET_KEY, start, end
            )

            if not curriculum_ids:
                return None

            # 각 아이템의 상세 정보 조회
            feed_items = []
            for curriculum_id in curriculum_ids:
                cache_key = f"{self.CACHE_KEY_PREFIX}:item:{curriculum_id}"
                cached_data = await redis_client.get(cache_key)

                if cached_data:
                    item_data = json.loads(cached_data)
                    feed_item = FeedItem.from_dict(item_data)

                    # 필터링 적용
                    if self._matches_filter(feed_item, feed_filter):
                        feed_items.append(feed_item)

            # 전체 개수는 Sorted Set 크기로 추정
            total_count = await redis_client.redis.zcard(self.SORTED_SET_KEY)  # type: ignore

            return total_count, feed_items

        except Exception:
            # 캐시 오류 시 None 반환하여 DB 조회로 fallback
            return None

    async def _get_from_database(
        self, feed_filter: FeedFilter
    ) -> Tuple[int, List[FeedItem]]:
        """데이터베이스에서 피드 조회"""
        base_query = (
            select(CurriculumModel)
            .where(CurriculumModel.visibility == "PUBLIC")
            .options(
                selectinload(CurriculumModel.week_schedules),
                joinedload(CurriculumModel.user),
            )
        )

        # 필터링 적용
        if feed_filter.category_id:
            base_query = base_query.join(CurriculumCategoryModel).where(
                CurriculumCategoryModel.category_id == feed_filter.category_id
            )

        if feed_filter.tags:
            base_query = (
                base_query.join(CurriculumTagModel)
                .join(TagModel)
                .where(TagModel.name.in_(feed_filter.tags))
                .group_by(CurriculumModel.id)
                .having(func.count(TagModel.id) == len(feed_filter.tags))
            )

        if feed_filter.search_query:
            search_term = f"%{feed_filter.search_query}%"
            base_query = base_query.where(
                or_(
                    CurriculumModel.title.like(search_term),
                    CurriculumModel.user.has(UserModel.name.like(search_term)),
                )
            )

        # 전체 개수
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.scalar(count_query) or 0

        # 페이지네이션 및 정렬
        paged_query = (
            base_query.order_by(CurriculumModel.updated_at.desc())
            .offset(feed_filter.offset)
            .limit(feed_filter.limit)
        )

        result = await self.session.execute(paged_query)
        curriculum_models = result.unique().scalars().all()

        # FeedItem으로 변환
        feed_items = []
        for curriculum in curriculum_models:
            # 카테고리 정보 조회
            category_info = await self._get_category_info(curriculum.id)

            # 태그 정보 조회
            tags = await self._get_curriculum_tags(curriculum.id)

            feed_item = FeedItem(
                curriculum_id=curriculum.id,
                title=curriculum.title,
                owner_id=curriculum.user_id,
                owner_name=curriculum.user.name,
                total_weeks=len(curriculum.week_schedules),
                total_lessons=sum(len(ws.lessons) for ws in curriculum.week_schedules),
                created_at=curriculum.created_at,
                updated_at=curriculum.updated_at,
                score=curriculum.updated_at.timestamp(),
                category_name=category_info[0] if category_info else None,
                category_color=category_info[1] if category_info else None,
                tags=tags,
            )
            feed_items.append(feed_item)

        return total_count, feed_items

    async def _get_category_info(self, curriculum_id: str) -> Optional[Tuple[str, str]]:
        """커리큘럼의 카테고리 정보 조회"""
        query: Select[Tuple[str, str]] = (
            select(CategoryModel.name, CategoryModel.color)
            .join(CurriculumCategoryModel)
            .where(CurriculumCategoryModel.curriculum_id == curriculum_id)
        )
        result: Result[Tuple[str, str]] = await self.session.execute(query)
        return result.first()  # type: ignore

    async def _get_curriculum_tags(self, curriculum_id: str) -> List[str]:
        """커리큘럼의 태그 목록 조회"""
        query = (
            select(TagModel.name)
            .join(CurriculumTagModel)
            .where(CurriculumTagModel.curriculum_id == curriculum_id)
        )
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]

    def _matches_filter(self, feed_item: FeedItem, feed_filter: FeedFilter) -> bool:
        """피드 아이템이 필터 조건에 맞는지 확인"""
        if feed_filter.search_query:
            search_lower = feed_filter.search_query.lower()
            if (
                search_lower not in feed_item.title.lower()
                and search_lower not in feed_item.owner_name.lower()
            ):
                return False

        if feed_filter.tags:
            if not all(tag in feed_item.tags for tag in feed_filter.tags):  # type: ignore
                return False

        return True

    async def _cache_feed_items(
        self, feed_items: List[FeedItem], feed_filter: FeedFilter
    ) -> None:
        """피드 아이템들을 캐시에 저장"""
        try:
            # Sorted Set에 추가
            mapping = {item.curriculum_id: item.feed_score for item in feed_items}
            if mapping:
                await redis_client.zadd(self.SORTED_SET_KEY, mapping)
                await redis_client.expire(self.SORTED_SET_KEY, self.CACHE_EXPIRE_TIME)

            # 개별 아이템 캐시
            for item in feed_items:
                await self.cache_feed_item(item)

        except Exception:
            # 캐시 오류는 무시 (DB 조회는 성공했으므로)
            pass

    async def cache_feed_item(self, feed_item: FeedItem) -> None:
        """단일 피드 아이템 캐시"""
        try:
            cache_key = f"{self.CACHE_KEY_PREFIX}:item:{feed_item.curriculum_id}"
            item_data = json.dumps(feed_item.to_dict(), ensure_ascii=False)
            await redis_client.set(cache_key, item_data, ex=self.CACHE_EXPIRE_TIME)

            # Sorted Set에도 추가
            await redis_client.zadd(
                self.SORTED_SET_KEY, {feed_item.curriculum_id: feed_item.feed_score}
            )

        except Exception:
            # 캐시 오류는 무시
            pass

    async def remove_from_cache(self, curriculum_id: str) -> None:
        """캐시에서 피드 아이템 제거"""
        try:
            # 개별 아이템 캐시 삭제
            cache_key = f"{self.CACHE_KEY_PREFIX}:item:{curriculum_id}"
            await redis_client.delete(cache_key)

            # Sorted Set에서 제거
            await redis_client.zrem(self.SORTED_SET_KEY, curriculum_id)

        except Exception:
            # 캐시 오류는 무시
            pass

    async def invalidate_feed_cache(self) -> None:
        """전체 피드 캐시 무효화"""
        try:
            # Sorted Set 삭제
            await redis_client.delete(self.SORTED_SET_KEY)

        except Exception:
            # 캐시 오류는 무시
            pass

    async def warm_up_cache(self, limit: int = 100) -> None:
        """캐시 워밍업 - 최신 커리큘럼들을 미리 캐시에 로드"""
        try:
            # 최신 공개 커리큘럼들 조회
            query = (
                select(CurriculumModel)
                .where(CurriculumModel.visibility == "PUBLIC")
                .order_by(CurriculumModel.updated_at.desc())
                .limit(limit)
                .options(
                    selectinload(CurriculumModel.week_schedules),
                    joinedload(CurriculumModel.user),
                )
            )

            result = await self.session.execute(query)
            curriculums = result.unique().scalars().all()

            # 캐시에 저장
            for curriculum in curriculums:
                category_info = await self._get_category_info(curriculum.id)
                tags = await self._get_curriculum_tags(curriculum.id)

                feed_item = FeedItem(
                    curriculum_id=curriculum.id,
                    title=curriculum.title,
                    owner_id=curriculum.user_id,
                    owner_name=curriculum.user.name,
                    total_weeks=len(curriculum.week_schedules),
                    total_lessons=sum(
                        len(ws.lessons) for ws in curriculum.week_schedules
                    ),
                    created_at=curriculum.created_at,
                    updated_at=curriculum.updated_at,
                    score=curriculum.updated_at.timestamp(),
                    category_name=category_info[0] if category_info else None,
                    category_color=category_info[1] if category_info else None,
                    tags=tags,
                )

                await self.cache_feed_item(feed_item)

        except Exception as e:
            # 캐시 워밍업 실패는 로그만 남기고 계속 진행
            print(f"Cache warm-up failed: {e}")

    async def get_cache_stats(self) -> dict:
        """캐시 통계 조회"""
        try:
            # Sorted Set 크기
            total_cached = await redis_client.redis.zcard(self.SORTED_SET_KEY)  # type: ignore

            # TTL 확인
            ttl = await redis_client.redis.ttl(self.SORTED_SET_KEY)  # type: ignore

            return {
                "total_cached_items": total_cached,
                "cache_ttl_seconds": ttl,
                "cache_key": self.SORTED_SET_KEY,
            }
        except Exception:
            return {"error": "Unable to get cache stats"}
