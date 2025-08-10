from datetime import datetime
from typing import Any, List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel
from app.modules.learning.domain.repository.feedback_repo import IFeedbackRepository
from app.modules.learning.domain.vo.feedback_comment import FeedbackComment
from app.modules.learning.domain.vo.feedback_score import FeedbackScore
from app.modules.learning.infrastructure.db_model.feedback import FeedbackModel
from app.modules.learning.domain.entity.feedback import Feedback as FeedbackDomain
from app.modules.learning.infrastructure.db_model.summary import SummaryModel


class FeedbackRepository(IFeedbackRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, feedback_model: FeedbackModel) -> FeedbackDomain:

        return FeedbackDomain(
            id=feedback_model.id,
            summary_id=feedback_model.summary_id,
            comment=FeedbackComment(feedback_model.comment),
            score=FeedbackScore(feedback_model.score),
            created_at=feedback_model.created_at,
            updated_at=feedback_model.updated_at,
        )

    async def save(self, feedback: FeedbackDomain) -> None:

        new_feedback = FeedbackModel(  # type: ignore
            id=feedback.id,
            summary_id=feedback.summary_id,
            comment=feedback.comment.value,
            score=feedback.score.value,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
        )

        self.session.add(new_feedback)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, feedback_id: str) -> Optional[FeedbackDomain]:

        query = select(FeedbackModel).where(FeedbackModel.id == feedback_id)
        result: Result[Tuple[FeedbackModel]] = await self.session.execute(query)
        feedback_model: FeedbackModel | None = result.scalar_one_or_none()

        if not feedback_model:
            return None

        return self._to_domain(feedback_model)

    async def find_by_summary_id(self, summary_id: str) -> Optional[FeedbackDomain]:

        query: Select[Tuple[FeedbackModel]] = select(FeedbackModel).where(
            FeedbackModel.summary_id == summary_id
        )
        result: Result[Tuple[FeedbackModel]] = await self.session.execute(query)
        feedback_model: FeedbackModel | None = result.scalar_one_or_none()

        if not feedback_model:
            return None

        return self._to_domain(feedback_model)

    async def find_by_curriculum(
        self,
        curriculum_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[FeedbackDomain]]:

        # SummaryModel과 조인하여 curriculum_id 확인
        base_query: Select[Tuple[FeedbackModel]] = (
            select(FeedbackModel)
            .join(SummaryModel)
            .where(SummaryModel.curriculum_id == curriculum_id)
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[FeedbackModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(FeedbackModel.created_at.desc())
        )

        result: Result[Tuple[FeedbackModel]] = await self.session.execute(paged_query)
        feedback_models: Sequence[FeedbackModel] = result.scalars().all()

        feedbacks: List[FeedbackDomain] = [
            self._to_domain(model) for model in feedback_models
        ]
        return total_count, feedbacks

    async def find_by_user(
        self,
        owner_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[FeedbackDomain]]:

        # SummaryModel, CurriculumModel과 조인하여 owner_id 확인
        base_query: Select[Tuple[FeedbackModel]] = (
            select(FeedbackModel)
            .join(SummaryModel)
            .join(CurriculumModel)
            .where(CurriculumModel.user_id == owner_id)
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[FeedbackModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(FeedbackModel.created_at.desc())
        )

        result: Result[Tuple[FeedbackModel]] = await self.session.execute(paged_query)
        feedback_models: Sequence[FeedbackModel] = result.scalars().all()

        feedbacks: List[FeedbackDomain] = [
            self._to_domain(model) for model in feedback_models
        ]
        return total_count, feedbacks

    async def find_by_score_range(
        self,
        min_score: float,
        max_score: float,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[FeedbackDomain]]:

        base_query: Select[Tuple[FeedbackModel]] = select(FeedbackModel).where(
            and_(
                FeedbackModel.score >= min_score,
                FeedbackModel.score <= max_score,
            )
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[FeedbackModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(FeedbackModel.score.desc(), FeedbackModel.created_at.desc())
        )

        result: Result[Tuple[FeedbackModel]] = await self.session.execute(paged_query)
        feedback_models: Sequence[FeedbackModel] = result.scalars().all()

        feedbacks: List[FeedbackDomain] = [
            self._to_domain(model) for model in feedback_models
        ]
        return total_count, feedbacks

    async def update(self, feedback: FeedbackDomain) -> None:

        existing_feedback: FeedbackModel | None = await self.session.get(
            FeedbackModel, feedback.id
        )
        if not existing_feedback:
            raise ValueError(f"Feedback {feedback.id} not found")

        existing_feedback.comment = feedback.comment.value
        existing_feedback.score = feedback.score.value
        existing_feedback.updated_at = feedback.updated_at

        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete(self, feedback_id: str) -> None:

        existing_feedback: FeedbackModel | None = await self.session.get(
            FeedbackModel, feedback_id
        )
        if existing_feedback:
            await self.session.delete(existing_feedback)
            try:
                await self.session.commit()
            except:
                await self.session.rollback()
                raise

    async def count_by_curriculum(self, curriculum_id: str) -> int:

        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(FeedbackModel)
            .join(SummaryModel)
            .where(SummaryModel.curriculum_id == curriculum_id)
        )
        return await self.session.scalar(query) or 0

    async def count_by_user(self, owner_id: str) -> int:

        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(FeedbackModel)
            .join(SummaryModel)
            .join(CurriculumModel)
            .where(CurriculumModel.user_id == owner_id)
        )
        return await self.session.scalar(query) or 0

    async def get_average_score_by_curriculum(
        self, curriculum_id: str
    ) -> Optional[float]:

        query: Select[Tuple[Any]] = (
            select(func.avg(FeedbackModel.score))
            .select_from(FeedbackModel)
            .join(SummaryModel)
            .where(SummaryModel.curriculum_id == curriculum_id)
        )
        result: Any | None = await self.session.scalar(query)
        return float(result) if result is not None else None

    async def get_average_score_by_user(self, owner_id: str) -> Optional[float]:

        query: Select[Tuple[Any]] = (
            select(func.avg(FeedbackModel.score))
            .select_from(FeedbackModel)
            .join(SummaryModel)
            .join(CurriculumModel)
            .where(CurriculumModel.user_id == owner_id)
        )
        result: Any | None = await self.session.scalar(query)
        return float(result) if result is not None else None

    async def exists_by_summary_id(self, summary_id: str) -> bool:

        query: Select[Tuple[FeedbackModel]] = select(FeedbackModel).where(
            FeedbackModel.summary_id == summary_id
        )
        result: Result[Tuple[FeedbackModel]] = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_by_user_since(self, owner_id: str, since_date: datetime) -> int:
        """특정 날짜 이후 사용자의 피드백 개수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(FeedbackModel)
            .join(SummaryModel)
            .join(CurriculumModel)
            .where(
                and_(
                    CurriculumModel.user_id == owner_id,
                    FeedbackModel.created_at >= since_date,
                )
            )
        )
        return await self.session.scalar(query) or 0

    async def find_by_user_since(
        self,
        owner_id: str,
        since_date: datetime,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[FeedbackDomain]]:
        """특정 날짜 이후 사용자의 피드백 목록 조회"""
        base_query: Select[Tuple[FeedbackModel]] = (
            select(FeedbackModel)
            .join(SummaryModel)
            .join(CurriculumModel)
            .where(
                and_(
                    CurriculumModel.user_id == owner_id,
                    FeedbackModel.created_at >= since_date,
                )
            )
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[FeedbackModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(FeedbackModel.created_at.desc())
        )

        result: Result[Tuple[FeedbackModel]] = await self.session.execute(paged_query)
        feedback_models: Sequence[FeedbackModel] = result.scalars().all()

        feedbacks: List[FeedbackDomain] = [
            self._to_domain(model) for model in feedback_models
        ]
        return total_count, feedbacks

    async def get_grade_distribution_by_user(self, owner_id: str) -> dict:
        """사용자의 등급별 피드백 분포 조회"""
        query = (
            select(
                case(
                    (FeedbackModel.score >= 9.0, "A+"),
                    (FeedbackModel.score >= 8.0, "A"),
                    (FeedbackModel.score >= 7.0, "B+"),
                    (FeedbackModel.score >= 6.0, "B"),
                    (FeedbackModel.score >= 5.0, "C+"),
                    (FeedbackModel.score >= 4.0, "C"),
                    else_="D",
                ).label("grade"),
                func.count().label("count"),
            )
            .select_from(FeedbackModel)
            .join(SummaryModel)
            .join(CurriculumModel)
            .where(CurriculumModel.user_id == owner_id)
            .group_by("grade")
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        # 기본 분포 딕셔너리 생성
        distribution: dict[str, int] = {
            "A+": 0,
            "A": 0,
            "B+": 0,
            "B": 0,
            "C+": 0,
            "C": 0,
            "D": 0,
        }

        # 실제 결과로 업데이트
        for row in rows:
            distribution[row.grade] = row.count  # type: ignore

        return distribution
