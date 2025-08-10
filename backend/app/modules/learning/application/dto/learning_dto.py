from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from app.modules.learning.domain.entity.summary import Summary
from app.modules.learning.domain.entity.feedback import Feedback


@dataclass
class CreateSummaryCommand:
    """요약 생성 명령"""

    curriculum_id: str
    week_number: int
    content: str
    owner_id: str


@dataclass
class UpdateSummaryCommand:
    """요약 수정 명령"""

    summary_id: str
    content: str
    owner_id: str


@dataclass
class CreateFeedbackCommand:
    """피드백 생성 명령"""

    summary_id: str
    comment: str
    score: float
    owner_id: str


@dataclass
class UpdateFeedbackCommand:
    """피드백 수정 명령"""

    feedback_id: str
    comment: str
    score: float
    owner_id: str


@dataclass
class SummaryQuery:
    """요약 조회 쿼리"""

    curriculum_id: Optional[str] = None
    week_number: Optional[int] = None
    owner_id: Optional[str] = None
    page: int = 1
    items_per_page: int = 10


@dataclass
class FeedbackQuery:
    """피드백 조회 쿼리"""

    curriculum_id: Optional[str] = None
    summary_id: Optional[str] = None
    owner_id: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    page: int = 1
    items_per_page: int = 10


@dataclass
class SummaryDTO:
    """요약 전송 객체"""

    id: str
    curriculum_id: str
    week_number: int
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, summary: Summary) -> "SummaryDTO":
        return cls(
            id=summary.id,
            curriculum_id=summary.curriculum_id,
            week_number=summary.week_number.value,
            content=summary.content.value,
            created_at=summary.created_at,
            updated_at=summary.updated_at,
        )


@dataclass
class FeedbackDTO:
    """피드백 전송 객체"""

    id: str
    summary_id: str
    comment: str
    score: float
    grade: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, feedback: Feedback) -> "FeedbackDTO":
        return cls(
            id=feedback.id,
            summary_id=feedback.summary_id,
            comment=feedback.comment.value,
            score=feedback.score.value,
            grade=feedback.get_grade(),
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
        )


@dataclass
class SummaryPageDTO:
    """요약 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    summaries: List[SummaryDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        summaries: List[Summary],
    ) -> "SummaryPageDTO":
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            summaries=[SummaryDTO.from_domain(s) for s in summaries],
        )


@dataclass
class FeedbackPageDTO:
    """피드백 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    feedbacks: List[FeedbackDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        feedbacks: List[Feedback],
    ) -> "FeedbackPageDTO":
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            feedbacks=[FeedbackDTO.from_domain(f) for f in feedbacks],
        )


@dataclass
class CurriculumStatsDTO:
    """커리큘럼 통계 전송 객체"""

    curriculum_id: str
    total_weeks: int
    completed_summaries: int
    received_feedbacks: int
    completion_rate: float
    feedback_rate: float
    average_score: Optional[float]
    score_distribution: Dict[str, int]
    weekly_progress: Dict[str, Dict]


@dataclass
class UserStatsDTO:
    """사용자 통계 전송 객체"""

    user_id: str
    total_summaries: int
    total_feedbacks: int
    average_score: Optional[float]
    recent_activity: Dict
    grade_distribution: Dict[str, int]
    learning_pattern: Dict
