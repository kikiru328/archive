from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.modules.learning.application.dto.learning_stats_dto import (
    UserLearningStatsDTO,
    CurriculumProgressDTO,
    LearningStreakDTO,
    ScoreDistributionDTO,
    RecentActivityDTO,
    MonthlyProgressDTO,
)


class CurriculumProgressResponse(BaseModel):
    """커리큘럼 진도 응답"""

    curriculum_id: str
    curriculum_title: str
    total_weeks: int
    completed_summaries: int
    received_feedbacks: int
    completion_rate: float = Field(description="요약 완료율 (%)")
    feedback_rate: float = Field(description="피드백 수신율 (%)")
    average_score: Optional[float]
    latest_activity: Optional[datetime]

    @classmethod
    def from_dto(cls, dto: CurriculumProgressDTO) -> "CurriculumProgressResponse":
        return cls(
            curriculum_id=dto.curriculum_id,
            curriculum_title=dto.curriculum_title,
            total_weeks=dto.total_weeks,
            completed_summaries=dto.completed_summaries,
            received_feedbacks=dto.received_feedbacks,
            completion_rate=round(dto.completion_rate, 1),
            feedback_rate=round(dto.feedback_rate, 1),
            average_score=round(dto.average_score, 1) if dto.average_score else None,
            latest_activity=dto.latest_activity,
        )


class LearningStreakResponse(BaseModel):
    """학습 연속성 응답"""

    current_streak: int = Field(description="현재 연속 학습 일수")
    longest_streak: int = Field(description="최장 연속 학습 일수")
    total_learning_days: int = Field(description="총 학습 일수")

    @classmethod
    def from_dto(cls, dto: LearningStreakDTO) -> "LearningStreakResponse":
        return cls(
            current_streak=dto.current_streak,
            longest_streak=dto.longest_streak,
            total_learning_days=dto.total_learning_days,
        )


class ScoreDistributionResponse(BaseModel):
    """점수 분포 응답"""

    grade_counts: Dict[str, int] = Field(description="등급별 개수")
    average_score: float = Field(description="평균 점수")
    highest_score: float = Field(description="최고 점수")
    lowest_score: float = Field(description="최저 점수")
    total_feedbacks: int = Field(description="총 피드백 수")

    @classmethod
    def from_dto(cls, dto: ScoreDistributionDTO) -> "ScoreDistributionResponse":
        return cls(
            grade_counts=dto.grade_counts,
            average_score=round(dto.average_score, 1),
            highest_score=round(dto.highest_score, 1),
            lowest_score=round(dto.lowest_score, 1),
            total_feedbacks=dto.total_feedbacks,
        )


class RecentActivityResponse(BaseModel):
    """최근 활동 응답"""

    type: str = Field(description="활동 타입 (summary/feedback)")
    curriculum_title: str
    week_number: Optional[int]
    content_snippet: str = Field(description="내용 미리보기")
    score: Optional[float]
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: RecentActivityDTO) -> "RecentActivityResponse":
        return cls(
            type=dto.type,
            curriculum_title=dto.curriculum_title,
            week_number=dto.week_number,
            content_snippet=dto.content_snippet,
            score=round(dto.score, 1) if dto.score else None,
            created_at=dto.created_at,
        )


class MonthlyProgressResponse(BaseModel):
    """월별 진도 응답"""

    month: str = Field(description="월 (YYYY-MM)")
    summaries_count: int = Field(description="요약 작성 수")
    feedbacks_count: int = Field(description="피드백 수신 수")
    average_score: Optional[float] = Field(description="평균 점수")

    @classmethod
    def from_dto(cls, dto: MonthlyProgressDTO) -> "MonthlyProgressResponse":
        return cls(
            month=dto.month,
            summaries_count=dto.summaries_count,
            feedbacks_count=dto.feedbacks_count,
            average_score=round(dto.average_score, 1) if dto.average_score else None,
        )


class UserLearningStatsResponse(BaseModel):
    """사용자 학습 통계 응답"""

    user_id: str
    stats_period_days: int = Field(description="통계 기간 (일수)")

    # 전체 요약
    total_summaries: int = Field(description="총 요약 수")
    total_feedbacks: int = Field(description="총 피드백 수")
    active_curriculums: int = Field(description="활성 커리큘럼 수")
    completed_curriculums: int = Field(description="완료된 커리큘럼 수")

    # 학습 연속성
    learning_streak: LearningStreakResponse

    # 점수 분석
    score_distribution: ScoreDistributionResponse

    # 커리큘럼별 진도
    curriculum_progress: List[CurriculumProgressResponse] = Field(
        description="커리큘럼별 진도 현황"
    )

    # 최근 활동
    recent_activities: List[RecentActivityResponse] = Field(
        description="최근 학습 활동"
    )

    # 월별 진도
    monthly_progress: List[MonthlyProgressResponse] = Field(
        description="월별 학습 진도"
    )

    # 목표 달성도
    weekly_goal_achievement: float = Field(description="주간 목표 달성률 (%)")

    # 생성 시간
    generated_at: datetime = Field(description="통계 생성 시간")

    @classmethod
    def from_dto(cls, dto: UserLearningStatsDTO) -> "UserLearningStatsResponse":
        return cls(
            user_id=dto.user_id,
            stats_period_days=dto.stats_period_days,
            total_summaries=dto.total_summaries,
            total_feedbacks=dto.total_feedbacks,
            active_curriculums=dto.active_curriculums,
            completed_curriculums=dto.completed_curriculums,
            learning_streak=LearningStreakResponse.from_dto(dto.learning_streak),
            score_distribution=ScoreDistributionResponse.from_dto(
                dto.score_distribution
            ),
            curriculum_progress=[
                CurriculumProgressResponse.from_dto(cp)
                for cp in dto.curriculum_progress
            ],
            recent_activities=[
                RecentActivityResponse.from_dto(ra) for ra in dto.recent_activities
            ],
            monthly_progress=[
                MonthlyProgressResponse.from_dto(mp) for mp in dto.monthly_progress
            ],
            weekly_goal_achievement=round(dto.weekly_goal_achievement, 1),
            generated_at=dto.generated_at,
        )
