from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app.modules.learning.application.dto.learning_stats_dto import (
    UserLearningStatsQuery,
    UserLearningStatsDTO,
    CurriculumProgressDTO,
    LearningStreakDTO,
    ScoreDistributionDTO,
    RecentActivityDTO,
    MonthlyProgressDTO,
)
from app.modules.learning.domain.repository.summary_repo import ISummaryRepository
from app.modules.learning.domain.repository.feedback_repo import IFeedbackRepository
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.user.domain.vo.role import RoleVO


class LearningStatsService:
    """학습 통계 애플리케이션 서비스"""

    def __init__(
        self,
        summary_repo: ISummaryRepository,
        feedback_repo: IFeedbackRepository,
        curriculum_repo: ICurriculumRepository,
    ) -> None:
        self.summary_repo = summary_repo
        self.feedback_repo = feedback_repo
        self.curriculum_repo = curriculum_repo

    def _is_recent_activity(
        self, activity_time: datetime, start_date: datetime
    ) -> bool:
        """timezone-safe datetime 비교"""
        # activity_time이 timezone-naive인 경우 UTC로 가정
        if activity_time.tzinfo is None:
            activity_time = activity_time.replace(tzinfo=timezone.utc)

        # start_date가 timezone-naive인 경우 UTC로 가정
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)

        return activity_time >= start_date

    async def get_user_learning_stats(
        self,
        query: UserLearningStatsQuery,
        role: RoleVO = RoleVO.USER,
    ) -> UserLearningStatsDTO:
        """사용자 학습 통계 조회"""

        # 기준 날짜 계산
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=query.days_ago)

        # 기본 통계 수집
        total_summaries = await self.summary_repo.count_by_user(query.user_id)
        total_feedbacks = await self.feedback_repo.count_by_user(query.user_id)

        # 사용자의 커리큘럼 목록 조회
        _, user_curriculums = await self.curriculum_repo.find_by_owner_id(
            owner_id=query.user_id, page=1, items_per_page=100  # 충분히 많이
        )

        # 커리큘럼별 진도 계산
        curriculum_progress = await self._calculate_curriculum_progress(
            user_curriculums, query.user_id
        )

        # 학습 연속성 계산
        learning_streak = await self._calculate_learning_streak(query.user_id, end_date)

        # 점수 분포 계산
        score_distribution = await self._calculate_score_distribution(query.user_id)

        # 최근 활동 조회
        recent_activities = await self._get_recent_activities(
            query.user_id, start_date, limit=10
        )

        # 월별 진도 계산
        monthly_progress = await self._calculate_monthly_progress(
            query.user_id, months=6
        )

        # 목표 달성도 계산 (주 3회 학습 목표 기준)
        weekly_goal_achievement = await self._calculate_weekly_goal_achievement(
            query.user_id, query.days_ago, target_days_per_week=3
        )

        # 완료된 커리큘럼 계산
        completed_curriculums = sum(
            1 for cp in curriculum_progress if cp.completion_rate >= 100.0
        )

        active_curriculums = len(
            [
                cp
                for cp in curriculum_progress
                if cp.latest_activity
                and self._is_recent_activity(cp.latest_activity, start_date)
            ]
        )

        return UserLearningStatsDTO(
            user_id=query.user_id,
            stats_period_days=query.days_ago,
            total_summaries=total_summaries,
            total_feedbacks=total_feedbacks,
            active_curriculums=active_curriculums,
            completed_curriculums=completed_curriculums,
            learning_streak=learning_streak,
            score_distribution=score_distribution,
            curriculum_progress=curriculum_progress,
            recent_activities=recent_activities,
            monthly_progress=monthly_progress,
            weekly_goal_achievement=weekly_goal_achievement,
            generated_at=end_date,
        )

    def _safe_datetime_key(self, dt: Optional[datetime]) -> datetime:
        """timezone-safe datetime key 생성"""
        if dt is None:
            return datetime(1900, 1, 1, tzinfo=timezone.utc)

        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)

        return dt

    async def _calculate_curriculum_progress(
        self, curriculums, user_id: str
    ) -> List[CurriculumProgressDTO]:
        """커리큘럼별 진도 계산"""
        progress_list = []

        for curriculum in curriculums:
            total_weeks = curriculum.get_total_weeks()

            # 해당 커리큘럼의 요약 수
            summary_count = await self.summary_repo.count_by_curriculum(curriculum.id)

            # 해당 커리큘럼의 피드백 수
            feedback_count = await self.feedback_repo.count_by_curriculum(curriculum.id)

            # 평균 점수
            avg_score = await self.feedback_repo.get_average_score_by_curriculum(
                curriculum.id
            )

            # 최근 활동 (요약 또는 피드백 중 가장 최근)
            total_count, recent_summaries = await self.summary_repo.find_by_curriculum(
                curriculum.id, page=1, items_per_page=1
            )
            latest_activity = None
            if recent_summaries:
                latest_activity = recent_summaries[0].created_at

            progress = CurriculumProgressDTO(
                curriculum_id=curriculum.id,
                curriculum_title=curriculum.title.value,
                total_weeks=total_weeks,
                completed_summaries=summary_count,
                received_feedbacks=feedback_count,
                completion_rate=(
                    (summary_count / total_weeks * 100) if total_weeks > 0 else 0
                ),
                feedback_rate=(
                    (feedback_count / summary_count * 100) if summary_count > 0 else 0
                ),
                average_score=avg_score,
                latest_activity=latest_activity,
            )
            progress_list.append(progress)

        # 최근 활동 순으로 정렬
        progress_list.sort(
            key=lambda x: self._safe_datetime_key(x.latest_activity),
            reverse=True,
        )

        return progress_list

    async def _calculate_learning_streak(
        self, user_id: str, end_date: datetime
    ) -> LearningStreakDTO:
        """학습 연속성 계산"""

        # 최근 100일간의 학습 활동 조회
        since_date = end_date - timedelta(days=100)
        total_count, recent_summaries = await self.summary_repo.find_by_user_since(
            owner_id=user_id, since_date=since_date, page=1, items_per_page=1000
        )

        # 날짜별 활동 그룹화
        activity_dates = set()
        for summary in recent_summaries:
            # timezone-aware datetime을 date로 변환
            summary_date = summary.created_at
            if summary_date.tzinfo is None:
                summary_date = summary_date.replace(tzinfo=timezone.utc)
            activity_dates.add(summary_date.date())

        # 현재 연속 학습 일수 계산
        current_streak = 0
        check_date = end_date.date()

        while check_date in activity_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

        # 최장 연속 학습 일수 계산
        longest_streak = 0
        temp_streak = 0

        # 과거 365일 체크
        for i in range(365):
            check_date = end_date.date() - timedelta(days=i)
            if check_date in activity_dates:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0

        total_learning_days = len(activity_dates)

        return LearningStreakDTO(
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_learning_days=total_learning_days,
        )

    async def _calculate_score_distribution(self, user_id: str) -> ScoreDistributionDTO:
        """점수 분포 계산"""

        # 사용자의 모든 피드백 조회
        total_count, feedbacks = await self.feedback_repo.find_by_user(
            owner_id=user_id, page=1, items_per_page=1000
        )

        if not feedbacks:
            return ScoreDistributionDTO(
                grade_counts={},
                average_score=0.0,
                highest_score=0.0,
                lowest_score=0.0,
                total_feedbacks=0,
            )

        # 등급별 개수 계산
        grade_counts = await self.feedback_repo.get_grade_distribution_by_user(user_id)

        scores = [f.score.value for f in feedbacks]

        return ScoreDistributionDTO(
            grade_counts=grade_counts,
            average_score=sum(scores) / len(scores),
            highest_score=max(scores),
            lowest_score=min(scores),
            total_feedbacks=len(feedbacks),
        )

    async def _get_recent_activities(
        self, user_id: str, since_date: datetime, limit: int = 10
    ) -> List[RecentActivityDTO]:
        """최근 활동 조회"""

        activities = []

        # 최근 요약들
        total_count, recent_summaries = await self.summary_repo.find_by_user_since(
            owner_id=user_id, since_date=since_date, page=1, items_per_page=limit
        )

        for summary in recent_summaries:
            # 커리큘럼 정보 조회 (간단히 하기 위해 ID만 사용)
            curriculum_title = f"Curriculum {summary.curriculum_id[:8]}"  # 간단한 제목

            activities.append(
                RecentActivityDTO(
                    type="summary",
                    curriculum_title=curriculum_title,
                    week_number=summary.week_number.value,
                    content_snippet=summary.get_content_snippet(100),
                    score=None,
                    created_at=summary.created_at,
                )
            )

        # 최근 피드백들
        total_count, recent_feedbacks = await self.feedback_repo.find_by_user_since(
            owner_id=user_id, since_date=since_date, page=1, items_per_page=limit
        )

        for feedback in recent_feedbacks:
            # 커리큘럼 정보 조회 (간단히 하기 위해 피드백에서 summary를 통해 가져올 수 있지만, 여기서는 간단히 처리)
            curriculum_title = (
                "Curriculum"  # 실제 구현시에는 summary를 통해 curriculum 조회 필요
            )

            activities.append(
                RecentActivityDTO(
                    type="feedback",
                    curriculum_title=curriculum_title,
                    week_number=None,
                    content_snippet=feedback.comment.value[:100],
                    score=feedback.score.value,
                    created_at=feedback.created_at,
                )
            )

        # 시간순 정렬 및 제한
        activities.sort(key=lambda x: x.created_at, reverse=True)
        return activities[:limit]

    async def _calculate_monthly_progress(
        self, user_id: str, months: int = 6
    ) -> List[MonthlyProgressDTO]:
        """월별 진도 계산"""

        end_date = datetime.now(timezone.utc)
        monthly_data = []

        for i in range(months):
            # 각 월의 시작과 끝 계산
            month_start = end_date.replace(day=1) - timedelta(days=30 * i)
            month_start = month_start.replace(day=1)

            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)

            # 해당 월의 요약 수
            summaries_count = await self.summary_repo.count_by_user_since(
                owner_id=user_id, since_date=month_start
            )

            # 해당 월의 피드백 수
            feedbacks_count = await self.feedback_repo.count_by_user_since(
                owner_id=user_id, since_date=month_start
            )

            # 해당 월의 평균 점수 (구현 필요시)
            avg_score = await self.feedback_repo.get_average_score_by_user(user_id)

            monthly_data.append(
                MonthlyProgressDTO(
                    month=month_start.strftime("%Y-%m"),
                    summaries_count=summaries_count,
                    feedbacks_count=feedbacks_count,
                    average_score=avg_score,
                )
            )

        return list(reversed(monthly_data))  # 오래된 순으로 정렬

    async def _calculate_weekly_goal_achievement(
        self, user_id: str, days: int, target_days_per_week: int = 3
    ) -> float:
        """주간 목표 달성률 계산"""

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # 해당 기간의 학습 활동일 수
        total_count, summaries = await self.summary_repo.find_by_user_since(
            owner_id=user_id, since_date=start_date, page=1, items_per_page=1000
        )

        activity_dates = set()
        for summary in summaries:
            summary_date = summary.created_at
            if summary_date.tzinfo is None:
                summary_date = summary_date.replace(tzinfo=timezone.utc)
            activity_dates.add(summary_date.date())

        actual_days = len(activity_dates)
        weeks = days / 7
        target_days = weeks * target_days_per_week

        if target_days == 0:
            return 0.0

        achievement = (actual_days / target_days) * 100
        return min(achievement, 100.0)  # 최대 100%
