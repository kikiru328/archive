from datetime import datetime, timezone
from typing import Optional

from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.learning.domain.entity.summary import Summary
from app.modules.learning.domain.entity.feedback import Feedback
from app.modules.learning.domain.repository.summary_repo import ISummaryRepository
from app.modules.learning.domain.repository.feedback_repo import IFeedbackRepository
from app.modules.learning.domain.vo.summary_content import SummaryContent
from app.modules.learning.domain.vo.feedback_comment import FeedbackComment
from app.modules.learning.domain.vo.feedback_score import FeedbackScore
from app.modules.curriculum.domain.vo.week_number import WeekNumber
from app.modules.user.domain.vo.role import RoleVO


class LearningDomainService:
    """Learning 도메인 서비스"""

    def __init__(
        self,
        summary_repo: ISummaryRepository,
        feedback_repo: IFeedbackRepository,
        curriculum_repo: ICurriculumRepository,
    ) -> None:
        self.summary_repo: ISummaryRepository = summary_repo
        self.feedback_repo: IFeedbackRepository = feedback_repo
        self.curriculum_repo: ICurriculumRepository = curriculum_repo

    async def create_summary(
        self,
        summary_id: str,
        owner_id: str,
        curriculum_id: str,
        week_number: int,
        content: str,
        created_at: Optional[datetime] = None,
    ) -> Summary:
        """요약 생성"""
        now = created_at or datetime.now(timezone.utc)

        summary = Summary(
            id=summary_id,
            owner_id=owner_id,
            curriculum_id=curriculum_id,
            week_number=WeekNumber(week_number),
            content=SummaryContent(content),
            created_at=now,
            updated_at=now,
        )

        return summary

    async def create_feedback(
        self,
        feedback_id: str,
        summary_id: str,
        comment: str,
        score: float,
        created_at: Optional[datetime] = None,
    ) -> Feedback:
        """피드백 생성"""
        now = created_at or datetime.now(timezone.utc)

        feedback = Feedback(
            id=feedback_id,
            summary_id=summary_id,
            comment=FeedbackComment(comment),
            score=FeedbackScore(score),
            created_at=now,
            updated_at=now,
        )

        return feedback

    async def can_access_summary(
        self,
        summary: Summary,
        owner_id: str,
        role: RoleVO,
    ) -> bool:
        """요약 접근 권한 확인"""
        # 관리자는 모든 요약에 접근 가능
        if role == RoleVO.ADMIN:
            return True

        # 커리큘럼 소유자 확인
        # curriculum = await self.curriculum_repo.find_by_id(
        #     curriculum_id=summary.curriculum_id,
        #     role=role,
        #     owner_id=user_id,
        # )

        # if not curriculum:
        # return False

        # 커리큘럼 소유자이거나 공개 커리큘럼인 경우 접근 가능
        # return curriculum.is_owned_by(owner_id) or curriculum.is_public()
        return summary.owner_id == owner_id

    async def can_modify_summary(
        self,
        summary: Summary,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """요약 수정 권한 확인"""
        # 관리자는 모든 요약 수정 가능
        if role == RoleVO.ADMIN:
            return True

        # 커리큘럼 소유자만 요약 수정 가능
        curriculum = await self.curriculum_repo.find_by_id(
            curriculum_id=summary.curriculum_id,
            role=role,
            owner_id=user_id,
        )

        if curriculum is None:
            return False
        return curriculum.is_owned_by(user_id)

    async def can_access_feedback(
        self,
        feedback: Feedback,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """피드백 접근 권한 확인"""
        # 관리자는 모든 피드백에 접근 가능
        if role == RoleVO.ADMIN:
            return True

        # 요약을 통해 커리큘럼 소유자 확인
        summary = await self.summary_repo.find_by_id(feedback.summary_id)
        if not summary:
            return False

        return await self.can_access_summary(summary, user_id, role)

    async def can_modify_feedback(
        self,
        feedback: Feedback,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """피드백 수정 권한 확인"""
        # 관리자는 모든 피드백 수정 가능
        if role == RoleVO.ADMIN:
            return True

        # 요약을 통해 커리큘럼 소유자 확인
        summary = await self.summary_repo.find_by_id(feedback.summary_id)
        if not summary:
            return False

        return await self.can_modify_summary(summary, user_id, role)

    async def validate_week_exists_in_curriculum(
        self,
        curriculum_id: str,
        week_number: int,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """커리큘럼에 해당 주차가 존재하는지 확인"""
        curriculum = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id,
        )

        if not curriculum:
            return False

        return curriculum.has_week(WeekNumber(week_number))

    async def get_curriculum_learning_progress(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> dict:
        """커리큘럼 학습 진도 조회"""
        curriculum = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id,
        )

        if not curriculum:
            return {}

        total_weeks = curriculum.get_total_weeks()
        summary_count = await self.summary_repo.count_by_curriculum(curriculum_id)
        feedback_count = await self.feedback_repo.count_by_curriculum(curriculum_id)
        average_score = await self.feedback_repo.get_average_score_by_curriculum(
            curriculum_id
        )

        return {
            "total_weeks": total_weeks,
            "completed_summaries": summary_count,
            "received_feedbacks": feedback_count,
            "completion_rate": (
                (summary_count / total_weeks) * 100 if total_weeks > 0 else 0
            ),
            "average_score": average_score,
        }
