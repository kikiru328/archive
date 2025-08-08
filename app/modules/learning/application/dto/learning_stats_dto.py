from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class UserLearningStatsQuery:
    """사용자 학습 통계 조회 쿼리"""

    user_id: str
    days_ago: int = 30  # 최근 N일 기준


@dataclass
class CurriculumProgressDTO:
    """커리큘럼별 진도 정보"""

    curriculum_id: str
    curriculum_title: str
    total_weeks: int
    completed_summaries: int
    received_feedbacks: int
    completion_rate: float  # 요약 완료율 (%)
    feedback_rate: float  # 피드백 수신율 (%)
    average_score: Optional[float]
    latest_activity: Optional[datetime]


@dataclass
class LearningStreakDTO:
    """학습 연속 기록"""

    current_streak: int  # 현재 연속 학습 일수
    longest_streak: int  # 최장 연속 학습 일수
    total_learning_days: int  # 총 학습 일수


@dataclass
class ScoreDistributionDTO:
    """점수 분포"""

    grade_counts: Dict[str, int]  # {"A+": 5, "A": 3, ...}
    average_score: float
    highest_score: float
    lowest_score: float
    total_feedbacks: int


@dataclass
class RecentActivityDTO:
    """최근 활동"""

    type: str  # "summary" | "feedback"
    curriculum_title: str
    week_number: Optional[int]
    content_snippet: str
    score: Optional[float]
    created_at: datetime


@dataclass
class MonthlyProgressDTO:
    """월별 진도"""

    month: str  # "2024-01"
    summaries_count: int
    feedbacks_count: int
    average_score: Optional[float]


@dataclass
class UserLearningStatsDTO:
    """사용자 학습 통계 전체"""

    user_id: str
    stats_period_days: int

    # 전체 요약
    total_summaries: int
    total_feedbacks: int
    active_curriculums: int
    completed_curriculums: int  # 모든 주차에 요약이 있는 커리큘럼

    # 학습 연속성
    learning_streak: LearningStreakDTO

    # 점수 분석
    score_distribution: ScoreDistributionDTO

    # 커리큘럼별 진도
    curriculum_progress: List[CurriculumProgressDTO]

    # 최근 활동
    recent_activities: List[RecentActivityDTO]

    # 월별 진도 (최근 6개월)
    monthly_progress: List[MonthlyProgressDTO]

    # 목표 달성도
    weekly_goal_achievement: float  # 주간 목표 달성률 (예: 주 3회 학습)

    # 생성 시간
    generated_at: datetime
