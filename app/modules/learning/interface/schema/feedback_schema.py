from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.modules.learning.application.dto.learning_dto import (
    CreateFeedbackCommand,
    UpdateFeedbackCommand,
    FeedbackDTO,
    FeedbackPageDTO,
)


class CreateFeedbackRequest(BaseModel):
    """피드백 생성 요청 (수동)"""

    comment: str = Field(min_length=10, max_length=2000, description="피드백 코멘트")
    score: float = Field(ge=0.0, le=10.0, description="피드백 점수 (0.0 ~ 10.0)")

    def to_command(self, summary_id: str, owner_id: str) -> CreateFeedbackCommand:
        return CreateFeedbackCommand(
            summary_id=summary_id,
            comment=self.comment,
            score=self.score,
            owner_id=owner_id,
        )


class UpdateFeedbackRequest(BaseModel):
    """피드백 수정 요청"""

    comment: str = Field(
        min_length=10, max_length=2000, description="수정할 피드백 코멘트"
    )
    score: float = Field(ge=0.0, le=10.0, description="수정할 피드백 점수 (0.0 ~ 10.0)")

    def to_command(self, feedback_id: str, owner_id: str) -> UpdateFeedbackCommand:
        return UpdateFeedbackCommand(
            feedback_id=feedback_id,
            comment=self.comment,
            score=self.score,
            owner_id=owner_id,
        )


class FeedbackResponse(BaseModel):
    """피드백 응답"""

    id: str
    summary_id: str
    comment: str
    score: float
    grade: str
    comment_snippet: str
    is_good_score: bool
    is_poor_score: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: FeedbackDTO) -> "FeedbackResponse":
        comment_snippet = (
            dto.comment[:100] + "..." if len(dto.comment) > 100 else dto.comment
        )
        return cls(
            id=dto.id,
            summary_id=dto.summary_id,
            comment=dto.comment,
            score=dto.score,
            grade=dto.grade,
            comment_snippet=comment_snippet,
            is_good_score=dto.score >= 7.0,
            is_poor_score=dto.score <= 4.0,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class FeedbackBriefResponse(BaseModel):
    """피드백 요약 응답 (목록용)"""

    id: str
    summary_id: str
    comment_snippet: str
    score: float
    grade: str
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: FeedbackDTO) -> "FeedbackBriefResponse":
        comment_snippet = (
            dto.comment[:80] + "..." if len(dto.comment) > 80 else dto.comment
        )
        return cls(
            id=dto.id,
            summary_id=dto.summary_id,
            comment_snippet=comment_snippet,
            score=dto.score,
            grade=dto.grade,
            created_at=dto.created_at,
        )


class FeedbackPageResponse(BaseModel):
    """피드백 목록 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    feedbacks: List[FeedbackBriefResponse]
    average_score: Optional[float] = None

    @classmethod
    def from_dto(
        cls, dto: FeedbackPageDTO, average_score: Optional[float] = None
    ) -> "FeedbackPageResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            feedbacks=[FeedbackBriefResponse.from_dto(f) for f in dto.feedbacks],
            average_score=average_score,
        )


class GenerateFeedbackRequest(BaseModel):
    """AI 피드백 생성 요청 (자동)"""

    # 요청 본문 없음 - summary_id는 경로에서 가져옴
    pass
