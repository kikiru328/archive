from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.modules.taxonomy.application.dto.tag_dto import (
    CreateTagCommand,
    UpdateTagCommand,
    CreateCategoryCommand,
    UpdateCategoryCommand,
    AddTagsToCurriculumCommand,
    RemoveTagFromCurriculumCommand,
    AssignCategoryToCurriculumCommand,
    TagDTO,
    CategoryDTO,
    TagPageDTO,
    CategoryPageDTO,
    CurriculumTagsDTO,
)


# ========================= TAG SCHEMAS =========================


class CreateTagRequest(BaseModel):
    """태그 생성 요청"""

    name: str = Field(min_length=1, max_length=20, description="태그 이름")

    def to_command(self, created_by: str) -> CreateTagCommand:
        return CreateTagCommand(
            name=self.name,
            created_by=created_by,
        )


class UpdateTagRequest(BaseModel):
    """태그 수정 요청"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=20, description="태그 이름"
    )

    def to_command(self, tag_id: str) -> UpdateTagCommand:
        return UpdateTagCommand(
            tag_id=tag_id,
            name=self.name,
        )


class TagResponse(BaseModel):
    """태그 응답"""

    id: str
    name: str
    usage_count: int
    is_popular: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: TagDTO) -> "TagResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            usage_count=dto.usage_count,
            is_popular=dto.is_popular,
            created_by=dto.created_by,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class TagBriefResponse(BaseModel):
    """태그 간략 응답 (목록용)"""

    id: str
    name: str
    usage_count: int
    is_popular: bool

    @classmethod
    def from_dto(cls, dto: TagDTO) -> "TagBriefResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            usage_count=dto.usage_count,
            is_popular=dto.is_popular,
        )


class TagPageResponse(BaseModel):
    """태그 목록 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    tags: List[TagBriefResponse]

    @classmethod
    def from_dto(cls, dto: TagPageDTO) -> "TagPageResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            tags=[TagBriefResponse.from_dto(tag) for tag in dto.tags],
        )


class TagSearchResponse(BaseModel):
    """태그 검색 응답 (자동완성용)"""

    suggestions: List[TagBriefResponse]

    @classmethod
    def from_dto_list(cls, tags: List[TagDTO]) -> "TagSearchResponse":
        return cls(suggestions=[TagBriefResponse.from_dto(tag) for tag in tags])


# ========================= CATEGORY SCHEMAS =========================


class CreateCategoryRequest(BaseModel):
    """카테고리 생성 요청"""

    name: str = Field(min_length=2, max_length=30, description="카테고리 이름")
    description: Optional[str] = Field(
        None, max_length=500, description="카테고리 설명"
    )
    color: str = Field(
        min_length=7, max_length=7, description="헥스 색상 코드 (예: #FF5733)"
    )
    icon: Optional[str] = Field(None, max_length=50, description="아이콘 이름")
    sort_order: int = Field(default=0, description="정렬 순서")

    def to_command(self) -> CreateCategoryCommand:
        return CreateCategoryCommand(
            name=self.name,
            description=self.description,
            color=self.color,
            icon=self.icon,
            sort_order=self.sort_order,
        )


class UpdateCategoryRequest(BaseModel):
    """카테고리 수정 요청"""

    name: Optional[str] = Field(
        None, min_length=2, max_length=30, description="카테고리 이름"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="카테고리 설명"
    )
    color: Optional[str] = Field(
        None, min_length=7, max_length=7, description="헥스 색상 코드"
    )
    icon: Optional[str] = Field(None, max_length=50, description="아이콘 이름")
    sort_order: Optional[int] = Field(None, description="정렬 순서")
    is_active: Optional[bool] = Field(None, description="활성화 여부")

    def to_command(self, category_id: str) -> UpdateCategoryCommand:
        return UpdateCategoryCommand(
            category_id=category_id,
            name=self.name,
            description=self.description,
            color=self.color,
            icon=self.icon,
            sort_order=self.sort_order,
            is_active=self.is_active,
        )


class CategoryResponse(BaseModel):
    """카테고리 응답"""

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
    def from_dto(cls, dto: CategoryDTO) -> "CategoryResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            color=dto.color,
            icon=dto.icon,
            sort_order=dto.sort_order,
            is_active=dto.is_active,
            usage_count=dto.usage_count,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class CategoryBriefResponse(BaseModel):
    """카테고리 간략 응답 (목록용)"""

    id: str
    name: str
    color: str
    icon: Optional[str]
    is_active: bool
    usage_count: int

    @classmethod
    def from_dto(cls, dto: CategoryDTO) -> "CategoryBriefResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            color=dto.color,
            icon=dto.icon,
            is_active=dto.is_active,
            usage_count=dto.usage_count,
        )


class CategoryPageResponse(BaseModel):
    """카테고리 목록 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    categories: List[CategoryBriefResponse]

    @classmethod
    def from_dto(cls, dto: CategoryPageDTO) -> "CategoryPageResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            categories=[CategoryBriefResponse.from_dto(cat) for cat in dto.categories],
        )


# ========================= CURRICULUM-TAG SCHEMAS =========================


class AddTagsRequest(BaseModel):
    """커리큘럼에 태그 추가 요청"""

    tag_names: List[str] = Field(
        min_items=1, max_items=10, description="추가할 태그 이름들"  # type: ignore
    )

    def to_command(
        self, curriculum_id: str, user_id: str
    ) -> AddTagsToCurriculumCommand:
        return AddTagsToCurriculumCommand(
            curriculum_id=curriculum_id,
            tag_names=self.tag_names,
            user_id=user_id,
        )


class RemoveTagRequest(BaseModel):
    """커리큘럼에서 태그 제거 요청"""

    tag_name: str = Field(min_length=1, max_length=20, description="제거할 태그 이름")

    def to_command(self, curriculum_id: str) -> RemoveTagFromCurriculumCommand:
        return RemoveTagFromCurriculumCommand(
            curriculum_id=curriculum_id,
            tag_name=self.tag_name,
        )


class AssignCategoryRequest(BaseModel):
    """커리큘럼에 카테고리 할당 요청"""

    category_id: str = Field(description="할당할 카테고리 ID")

    def to_command(
        self, curriculum_id: str, user_id: str
    ) -> AssignCategoryToCurriculumCommand:
        return AssignCategoryToCurriculumCommand(
            curriculum_id=curriculum_id,
            category_id=self.category_id,
            user_id=user_id,
        )


class CurriculumTagsResponse(BaseModel):
    """커리큘럼 태그/카테고리 응답"""

    curriculum_id: str
    tags: List[TagBriefResponse]
    category: Optional[CategoryBriefResponse]

    @classmethod
    def from_dto(cls, dto: CurriculumTagsDTO) -> "CurriculumTagsResponse":
        return cls(
            curriculum_id=dto.curriculum_id,
            tags=[TagBriefResponse.from_dto(tag) for tag in dto.tags],
            category=(
                CategoryBriefResponse.from_dto(dto.category) if dto.category else None
            ),
        )


# ========================= REORDER SCHEMAS =========================


class CategoryReorderItem(BaseModel):
    """카테고리 순서 변경 아이템"""

    id: str = Field(description="카테고리 ID")
    sort_order: int = Field(description="새 정렬 순서")


class CategoryReorderRequest(BaseModel):
    """카테고리 순서 변경 요청"""

    categories: List[CategoryReorderItem] = Field(
        min_items=1, description="순서를 변경할 카테고리들"  # type: ignore
    )


# ========================= STATISTICS SCHEMAS =========================


class TagStatisticsResponse(BaseModel):
    """태그 통계 응답"""

    total_tags: int
    popular_tags_count: int
    unused_tags_count: int
    most_popular_tags: List[str]


class CategoryStatisticsResponse(BaseModel):
    """카테고리 통계 응답"""

    total_categories: int
    active_categories: int
    inactive_categories: int
