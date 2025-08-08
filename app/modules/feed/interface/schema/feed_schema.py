from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel

from app.modules.feed.application.dto.feed_dto import (
    FeedItemDTO,
    FeedPageDTO,
)


class FeedItemResponse(BaseModel):
    """피드 아이템 응답"""

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
    tags: List[str] = []
    time_ago: str = ""  # "2시간 전", "3일 전" 등

    @classmethod
    def from_dto(cls, dto: FeedItemDTO) -> "FeedItemResponse":
        # 시간 차이 계산
        now = datetime.now(timezone.utc)
        if dto.updated_at.tzinfo is None:
            updated_at = dto.updated_at.replace(tzinfo=timezone.utc)
        else:
            # aware하면 UTC로 변환
            updated_at = dto.updated_at.astimezone(timezone.utc)

        time_diff = now - updated_at

        if time_diff.days > 0:
            time_ago = f"{time_diff.days}일 전"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            time_ago = f"{hours}시간 전"
        elif time_diff.seconds > 60:
            minutes = time_diff.seconds // 60
            time_ago = f"{minutes}분 전"
        else:
            time_ago = "방금 전"

        return cls(
            curriculum_id=dto.curriculum_id,
            title=dto.title,
            owner_id=dto.owner_id,
            owner_name=dto.owner_name,
            total_weeks=dto.total_weeks,
            total_lessons=dto.total_lessons,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            category_name=dto.category_name,
            category_color=dto.category_color,
            tags=dto.tags,  # type: ignore
            time_ago=time_ago,
        )


class FeedPageResponse(BaseModel):
    """피드 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    has_next: bool
    items: List[FeedItemResponse]

    @classmethod
    def from_dto(cls, dto: FeedPageDTO) -> "FeedPageResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            has_next=dto.has_next,
            items=[FeedItemResponse.from_dto(item) for item in dto.items],
        )
