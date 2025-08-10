from abc import ABCMeta, abstractmethod
from typing import List, Tuple

from app.modules.feed.domain.entity.feed_item import FeedItem
from app.modules.feed.domain.vo.feed_filter import FeedFilter


class IFeedRepository(metaclass=ABCMeta):
    @abstractmethod
    async def get_public_feed(
        self, feed_filter: FeedFilter
    ) -> Tuple[int, List[FeedItem]]:
        """공개 커리큘럼 피드 조회"""
        raise NotImplementedError

    @abstractmethod
    async def cache_feed_item(self, feed_item: FeedItem) -> None:
        """피드 아이템 캐시"""
        raise NotImplementedError

    @abstractmethod
    async def remove_from_cache(self, curriculum_id: str) -> None:
        """캐시에서 피드 아이템 제거"""
        raise NotImplementedError

    @abstractmethod
    async def invalidate_feed_cache(self) -> None:
        """전체 피드 캐시 무효화"""
        raise NotImplementedError
