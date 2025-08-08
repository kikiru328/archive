from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.entity.category import Category


# ========================= TAG DTOs =========================


@dataclass
class CreateTagCommand:
    """태그 생성 명령"""

    name: str
    created_by: str


@dataclass
class UpdateTagCommand:
    """태그 수정 명령"""

    tag_id: str
    name: Optional[str] = None


@dataclass
class TagQuery:
    """태그 조회 쿼리"""

    page: int = 1
    items_per_page: int = 20
    search_query: Optional[str] = None
    min_usage: int = 1


@dataclass
class TagDTO:
    """태그 전송 객체"""

    id: str
    name: str
    usage_count: int
    is_popular: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, tag: Tag, popular_threshold: int = 10) -> "TagDTO":
        return cls(
            id=tag.id,
            name=tag.name.value,
            usage_count=tag.usage_count,
            is_popular=tag.is_popular(popular_threshold),
            created_by=tag.created_by,
            created_at=tag.created_at,
            updated_at=tag.updated_at,
        )


@dataclass
class TagPageDTO:
    """태그 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    tags: List[TagDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        tags: List[Tag],
    ) -> "TagPageDTO":
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            tags=[TagDTO.from_domain(tag) for tag in tags],
        )


# ========================= CATEGORY DTOs =========================


@dataclass
class CreateCategoryCommand:
    """카테고리 생성 명령"""

    name: str
    description: Optional[str]
    color: str
    icon: Optional[str] = None
    sort_order: int = 0


@dataclass
class UpdateCategoryCommand:
    """카테고리 수정 명령"""

    category_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


@dataclass
class CategoryQuery:
    """카테고리 조회 쿼리"""

    page: int = 1
    items_per_page: int = 20
    include_inactive: bool = False


@dataclass
class CategoryDTO:
    """카테고리 전송 객체"""

    id: str
    name: str
    description: Optional[str]
    color: str
    icon: Optional[str]
    sort_order: int
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, category: Category, usage_count: int = 0) -> "CategoryDTO":
        return cls(
            id=category.id,
            name=category.name.value,
            description=category.description,
            color=category.color.value,
            icon=category.icon,
            sort_order=category.sort_order,
            is_active=category.is_active,
            usage_count=usage_count,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )


@dataclass
class CategoryPageDTO:
    """카테고리 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    categories: List[CategoryDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        categories: List[Category],
        usage_counts: Optional[List[int]] = None,
    ) -> "CategoryPageDTO":
        if usage_counts is None:
            usage_counts = [0] * len(categories)

        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            categories=[
                CategoryDTO.from_domain(category, usage_count)
                for category, usage_count in zip(categories, usage_counts)
            ],
        )


# ========================= CURRICULUM-TAG DTOs =========================


@dataclass
class AddTagsToCurriculumCommand:
    """커리큘럼에 태그 추가 명령"""

    curriculum_id: str
    tag_names: List[str]
    user_id: str


@dataclass
class RemoveTagFromCurriculumCommand:
    """커리큘럼에서 태그 제거 명령"""

    curriculum_id: str
    tag_name: str


@dataclass
class AssignCategoryToCurriculumCommand:
    """커리큘럼에 카테고리 할당 명령"""

    curriculum_id: str
    category_id: str
    user_id: str


@dataclass
class CurriculumTagsDTO:
    """커리큘럼의 태그들 전송 객체"""

    curriculum_id: str
    tags: List[TagDTO]
    category: Optional[CategoryDTO]

    @classmethod
    def from_domain(
        cls, curriculum_id: str, tags: List[Tag], category: Optional[Category] = None
    ) -> "CurriculumTagsDTO":
        return cls(
            curriculum_id=curriculum_id,
            tags=[TagDTO.from_domain(tag) for tag in tags],
            category=CategoryDTO.from_domain(category) if category else None,
        )


# ========================= STATISTICS DTOs =========================


@dataclass
class TagStatisticsDTO:
    """태그 통계 전송 객체"""

    total_tags: int
    popular_tags_count: int
    unused_tags_count: int
    most_popular_tags: List[str]


@dataclass
class CategoryStatisticsDTO:
    """카테고리 통계 전송 객체"""

    total_categories: int
    active_categories: int
    inactive_categories: int
