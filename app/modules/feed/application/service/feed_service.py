from app.modules.feed.application.dto.feed_dto import FeedQuery, FeedPageDTO
from app.modules.feed.domain.repository.feed_repo import IFeedRepository
from app.modules.feed.domain.vo.feed_filter import FeedFilter


class FeedService:
    """Feed 애플리케이션 서비스"""

    def __init__(self, feed_repo: IFeedRepository):
        self.feed_repo: IFeedRepository = feed_repo

    async def get_public_feed(self, query: FeedQuery) -> FeedPageDTO:
        """공개 커리큘럼 피드 조회"""
        feed_filter: FeedFilter = query.to_filter()
        total_count, feed_items = await self.feed_repo.get_public_feed(feed_filter)

        return FeedPageDTO.from_domain(
            total_count=total_count,
            page=query.page,
            items_per_page=query.items_per_page,
            feed_items=feed_items,
        )

    async def refresh_feed_item(self, curriculum_id: str) -> None:
        """특정 커리큘럼의 피드 아이템 갱신 (캐시 무효화)"""
        await self.feed_repo.remove_from_cache(curriculum_id)

    async def refresh_entire_feed(self) -> None:
        """전체 피드 갱신 (전체 캐시 무효화)"""
        await self.feed_repo.invalidate_feed_cache()
