from datetime import datetime
from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.curriculum.domain.vo.week_number import WeekNumber

from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel
from app.modules.learning.domain.repository.summary_repo import ISummaryRepository
from app.modules.learning.domain.vo.summary_content import SummaryContent
from app.modules.learning.infrastructure.db_model.summary import SummaryModel
from app.modules.learning.domain.entity.summary import Summary as SummaryDomain


class SummaryRepository(ISummaryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, summary_model: SummaryModel) -> SummaryDomain:
        return SummaryDomain(
            id=summary_model.id,
            curriculum_id=summary_model.curriculum_id,
            week_number=WeekNumber(summary_model.week_number),
            content=SummaryContent(summary_model.content),
            owner_id=summary_model.owner_id,
            created_at=summary_model.created_at,
            updated_at=summary_model.updated_at,
        )

    async def save(self, summary: SummaryDomain) -> None:
        new_summary = SummaryModel(  # type: ignore
            id=summary.id,
            curriculum_id=summary.curriculum_id,
            week_number=summary.week_number.value,
            content=summary.content.value,
            owner_id=summary.owner_id,
            created_at=summary.created_at,
            updated_at=summary.updated_at,
        )

        self.session.add(new_summary)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, summary_id: str) -> Optional[SummaryDomain]:

        query: Select[Tuple[SummaryModel]] = select(SummaryModel).where(
            SummaryModel.id == summary_id
        )
        result: Result[Tuple[SummaryModel]] = await self.session.execute(query)
        summary: SummaryModel | None = result.scalar_one_or_none()

        if not summary:
            return None
        return self._to_domain(summary)

    async def find_by_curriculum_and_week(
        self,
        curriculum_id: str,
        week_number: int,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[SummaryDomain]]:

        query: Select[Tuple[SummaryModel]] = select(SummaryModel).where(
            and_(
                SummaryModel.curriculum_id == curriculum_id,
                SummaryModel.week_number == week_number,
            )
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[SummaryModel]] = (
            query.limit(items_per_page)
            .offset(offset)
            .order_by(SummaryModel.created_at.desc())
        )

        result: Result[Tuple[SummaryModel]] = await self.session.execute(paged_query)
        summary_models: Sequence[SummaryModel] = result.scalars().all()

        summaries: List[SummaryDomain] = [
            self._to_domain(model) for model in summary_models
        ]
        return total_count, summaries

    async def find_by_curriculum(
        self,
        curriculum_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[SummaryDomain]]:

        base_query: Select[Tuple[SummaryModel]] = select(SummaryModel).where(
            SummaryModel.curriculum_id == curriculum_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[SummaryModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(SummaryModel.week_number.asc(), SummaryModel.created_at.desc())
        )

        result: Result[Tuple[SummaryModel]] = await self.session.execute(paged_query)
        summary_models: Sequence[SummaryModel] = result.scalars().all()

        summaries: List[SummaryDomain] = [
            self._to_domain(model) for model in summary_models
        ]
        return total_count, summaries

    async def find_by_user(
        self,
        owner_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[SummaryDomain]]:

        # CurriculumModel과 조인하여 owner_id 확인
        base_query: Select[Tuple[SummaryModel]] = (
            select(SummaryModel)
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
        paged_query: Select[Tuple[SummaryModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(SummaryModel.created_at.desc())
        )

        result: Result[Tuple[SummaryModel]] = await self.session.execute(paged_query)
        summary_models: Sequence[SummaryModel] = result.scalars().all()

        summaries: List[SummaryDomain] = [
            self._to_domain(model) for model in summary_models
        ]
        return total_count, summaries

    async def update(self, summary: SummaryDomain) -> None:

        existing_summary: SummaryModel | None = await self.session.get(
            SummaryModel, summary.id
        )
        if not existing_summary:
            raise ValueError(f"Summary {summary.id} not found")

        existing_summary.content = summary.content.value
        existing_summary.updated_at = summary.updated_at

        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete(self, summary_id: str) -> None:

        existing_summary: SummaryModel | None = await self.session.get(
            SummaryModel, summary_id
        )
        if existing_summary:
            await self.session.delete(existing_summary)
            try:
                await self.session.commit()
            except:
                await self.session.rollback()
                raise

    async def count_by_curriculum(self, curriculum_id: str) -> int:

        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(SummaryModel)
            .where(SummaryModel.curriculum_id == curriculum_id)
        )
        return await self.session.scalar(query) or 0

    async def count_by_user(self, owner_id: str) -> int:

        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(SummaryModel)
            .join(CurriculumModel)
            .where(CurriculumModel.user_id == owner_id)
        )
        return await self.session.scalar(query) or 0

    async def exists_by_id(self, summary_id: str) -> bool:

        existing_summary: SummaryModel | None = await self.session.get(
            SummaryModel, summary_id
        )
        return existing_summary is not None

    async def count_by_user_since(self, owner_id: str, since_date: datetime) -> int:
        """특정 날짜 이후 사용자의 요약 개수 조회"""
        query = (
            select(func.count())
            .select_from(SummaryModel)
            .join(CurriculumModel)
            .where(
                and_(
                    CurriculumModel.user_id == owner_id,
                    SummaryModel.created_at >= since_date,
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
    ) -> Tuple[int, List[SummaryDomain]]:
        """특정 날짜 이후 사용자의 요약 목록 조회"""
        base_query: Select[Tuple[SummaryModel]] = (
            select(SummaryModel)
            .join(CurriculumModel)
            .where(
                and_(
                    CurriculumModel.user_id == owner_id,
                    SummaryModel.created_at >= since_date,
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
        paged_query: Select[Tuple[SummaryModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(SummaryModel.created_at.desc())
        )

        result: Result[Tuple[SummaryModel]] = await self.session.execute(paged_query)
        summary_models: Sequence[SummaryModel] = result.scalars().all()

        summaries: List[SummaryDomain] = [
            self._to_domain(model) for model in summary_models
        ]
        return total_count, summaries
