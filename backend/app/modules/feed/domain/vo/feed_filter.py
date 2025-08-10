from dataclasses import dataclass
from typing import Optional


@dataclass
class FeedFilter:
    """피드 필터링 조건"""

    category_id: Optional[str] = None
    tags: Optional[list[str]] = None
    search_query: Optional[str] = None
    page: int = 1
    items_per_page: int = 20

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

        if self.items_per_page > 50:
            self.items_per_page = 50
        if self.items_per_page < 1:
            self.items_per_page = 1
        if self.page < 1:
            self.page = 1

    @property
    def offset(self) -> int:
        """페이지네이션 오프셋"""
        return (self.page - 1) * self.items_per_page

    @property
    def limit(self) -> int:
        """페이지네이션 리미트"""
        return self.items_per_page
