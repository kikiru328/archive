from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FeedItem:
    """피드 아이템 엔티티"""

    curriculum_id: str
    title: str
    owner_id: str
    owner_name: str
    total_weeks: int
    total_lessons: int
    created_at: datetime
    updated_at: datetime
    score: float  # Redis Sorted Set용 점수 (timestamp 기반)
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    tags: Optional[list[str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @property
    def feed_score(self) -> float:
        """피드 정렬을 위한 점수 계산 (최신순)"""
        return self.updated_at.timestamp()

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (Redis 저장용)"""
        return {
            "curriculum_id": self.curriculum_id,
            "title": self.title,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "total_weeks": self.total_weeks,
            "total_lessons": self.total_lessons,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "category_name": self.category_name,
            "category_color": self.category_color,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FeedItem":
        """딕셔너리에서 객체 생성 (Redis 조회용)"""
        return cls(
            curriculum_id=data["curriculum_id"],
            title=data["title"],
            owner_id=data["owner_id"],
            owner_name=data["owner_name"],
            total_weeks=data["total_weeks"],
            total_lessons=data["total_lessons"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            score=0.0,  # 임시값
            category_name=data.get("category_name"),
            category_color=data.get("category_color"),
            tags=data.get("tags", []),
        )
