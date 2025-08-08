from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from app.modules.learning.application.dto.learning_dto import (
    CreateSummaryCommand,
    UpdateSummaryCommand,
    SummaryDTO,
    SummaryPageDTO,
)


class CreateSummaryRequest(BaseModel):
    """요약 생성 요청"""

    content: str = Field(
        min_length=100,
        max_length=5000,
        description="요약 내용 (100자 이상 5000자 이하)",
    )

    def to_command(
        self, curriculum_id: str, week_number: int, owner_id: str
    ) -> CreateSummaryCommand:
        return CreateSummaryCommand(
            curriculum_id=curriculum_id,
            week_number=week_number,
            content=self.content,
            owner_id=owner_id,
        )


class UpdateSummaryRequest(BaseModel):
    """요약 수정 요청"""

    content: str = Field(
        min_length=100,
        max_length=5000,
        description="수정할 요약 내용 (100자 이상 5000자 이하)",
    )

    def to_command(self, summary_id: str, owner_id: str) -> UpdateSummaryCommand:
        return UpdateSummaryCommand(
            summary_id=summary_id,
            content=self.content,
            owner_id=owner_id,
        )


class SummaryResponse(BaseModel):
    """요약 응답"""

    id: str
    curriculum_id: str
    week_number: int
    content: str
    content_length: int
    snippet: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: SummaryDTO) -> "SummaryResponse":
        snippet = dto.content[:100] + "..." if len(dto.content) > 100 else dto.content
        return cls(
            id=dto.id,
            curriculum_id=dto.curriculum_id,
            week_number=dto.week_number,
            content=dto.content,
            content_length=len(dto.content),
            snippet=snippet,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class SummaryBriefResponse(BaseModel):
    """요약 요약 응답 (목록용)"""

    id: str
    curriculum_id: str
    week_number: int
    snippet: str
    content_length: int
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: SummaryDTO) -> "SummaryBriefResponse":
        snippet = dto.content[:150] + "..." if len(dto.content) > 150 else dto.content
        return cls(
            id=dto.id,
            curriculum_id=dto.curriculum_id,
            week_number=dto.week_number,
            snippet=snippet,
            content_length=len(dto.content),
            created_at=dto.created_at,
        )


class SummaryPageResponse(BaseModel):
    """요약 목록 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    summaries: List[SummaryBriefResponse]

    @classmethod
    def from_dto(cls, dto: SummaryPageDTO) -> "SummaryPageResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            summaries=[SummaryBriefResponse.from_dto(s) for s in dto.summaries],
        )
