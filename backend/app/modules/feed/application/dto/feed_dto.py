from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.modules.feed.domain.entity.feed_item import FeedItem
from app.modules.feed.domain.vo.feed_filter import FeedFilter


@dataclass
class FeedItemDTO:
    """피드 아이템 전송 객체"""

    curriculum_id: str
    title: str
    owner_id: str
    owner_name: str
    total_weeks: int
    total_lessons: int
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @classmethod
    def from_domain(cls, feed_item: FeedItem) -> "FeedItemDTO":
        return cls(
            curriculum_id=feed_item.curriculum_id,
            title=feed_item.title,
            owner_id=feed_item.owner_id,
            owner_name=feed_item.owner_name,
            total_weeks=feed_item.total_weeks,
            total_lessons=feed_item.total_lessons,
            created_at=feed_item.created_at,
            updated_at=feed_item.updated_at,
            category_name=feed_item.category_name,
            category_color=feed_item.category_color,
            tags=feed_item.tags,
        )


@dataclass
class FeedQuery:
    """피드 조회 쿼리"""

    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    search_query: Optional[str] = None
    page: int = 1
    items_per_page: int = 20

    def to_filter(self) -> FeedFilter:
        return FeedFilter(
            category_id=self.category_id,
            tags=self.tags,
            search_query=self.search_query,
            page=self.page,
            items_per_page=self.items_per_page,
        )


@dataclass
class FeedPageDTO:
    """피드 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    has_next: bool
    items: List[FeedItemDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        feed_items: List[FeedItem],
    ) -> "FeedPageDTO":
        has_next = (page * items_per_page) < total_count

        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            has_next=has_next,
            items=[FeedItemDTO.from_domain(item) for item in feed_items],
        )
