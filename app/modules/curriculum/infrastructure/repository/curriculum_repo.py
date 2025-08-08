from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, and_, func, select, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.curriculum.domain.entity.curriculum import (
    Curriculum as CurriculumDomain,
)
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.curriculum.domain.vo.lessons import Lessons
from app.modules.curriculum.domain.vo.title import Title
from app.modules.curriculum.domain.vo.visibility import Visibility
from app.modules.curriculum.domain.vo.week_number import WeekNumber
from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel
from app.modules.curriculum.infrastructure.db_model.week_schedule import (
    WeekScheduleModel,
)
from app.modules.user.domain.vo.role import RoleVO


class CurriculumRepository(ICurriculumRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, curriculum_model: CurriculumModel) -> CurriculumDomain:
        """DB Model -> Domain entity"""
        return CurriculumDomain(
            id=curriculum_model.id,
            owner_id=curriculum_model.user_id,
            title=Title(curriculum_model.title),
            week_schedules=[
                WeekSchedule(
                    week_number=WeekNumber(week_schedule.week_number),
                    lessons=Lessons(week_schedule.lessons),
                )
                for week_schedule in curriculum_model.week_schedules
            ],
            visibility=Visibility(curriculum_model.visibility),
            created_at=curriculum_model.created_at,
            updated_at=curriculum_model.updated_at,
        )

    async def save(self, curriculum: CurriculumDomain) -> None:
        new_curriculum = CurriculumModel(  # type: ignore
            id=str(curriculum.id),
            user_id=str(curriculum.owner_id),
            title=str(curriculum.title),
            visibility=curriculum.visibility.value,
            created_at=curriculum.created_at,
            updated_at=curriculum.updated_at,
        )

        for week_schedule in curriculum.week_schedules:
            new_curriculum.week_schedules.append(
                WeekScheduleModel(  # type: ignore
                    week_number=week_schedule.week_number.value,
                    lessons=week_schedule.lessons.items,
                )
            )
        self.session.add(new_curriculum)
        await self.session.commit()

    async def find_by_id(
        self,
        curriculum_id: str,
        role: RoleVO,
        owner_id: Optional[str] = None,
    ) -> Optional[CurriculumDomain]:

        query: Select[Tuple[CurriculumModel]] = (
            select(CurriculumModel)
            .where(CurriculumModel.id == curriculum_id)
            .options(
                selectinload(CurriculumModel.week_schedules),
                joinedload(CurriculumModel.user),
            )
        )

        if role != RoleVO.ADMIN:
            query = query.where(
                or_(
                    CurriculumModel.user_id == owner_id,
                    CurriculumModel.visibility == Visibility.PUBLIC.value,
                )
            )

        result: Result[Tuple[CurriculumModel]] = await self.session.execute(query)
        curriculum: CurriculumModel | None = result.scalars().first()

        if not curriculum:
            return None

        curriculum_entity: CurriculumDomain = self._to_domain(curriculum)
        setattr(curriculum_entity, "owner_name", curriculum.user.name)
        return curriculum_entity

    async def find_by_owner_id(
        self,
        owner_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[CurriculumDomain]]:

        total_count: int = await self.count_by_owner(owner_id=owner_id)
        query: Select[Tuple[CurriculumModel]] = (
            select(CurriculumModel)
            .where(CurriculumModel.user_id == owner_id)
            .options(selectinload(CurriculumModel.week_schedules))
            .order_by(CurriculumModel.created_at.desc())
            .offset((page - 1) * items_per_page)
            .limit(items_per_page)
        )
        result: Result[Tuple[CurriculumModel]] = await self.session.execute(query)
        curriculums: Sequence[CurriculumModel] = result.scalars().all()
        return (
            total_count,
            [self._to_domain(curriculum) for curriculum in curriculums],
        )

    async def find_public_curriculums(
        self,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[CurriculumDomain]]:

        total_count_query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(CurriculumModel)
            .where(CurriculumModel.visibility == Visibility.PUBLIC.value)
        )
        total: int = (await self.session.execute(total_count_query)).scalar_one()

        query: Select[Tuple[CurriculumModel]] = (
            select(CurriculumModel)
            .options(selectinload(CurriculumModel.week_schedules))
            .where(CurriculumModel.visibility == Visibility.PUBLIC.value)
            .order_by(CurriculumModel.created_at.desc())
            .offset((page - 1) * items_per_page)
            .limit(items_per_page)
        )
        result: Result[Tuple[CurriculumModel]] = await self.session.execute(query)
        models: Sequence[CurriculumModel] = result.scalars().all()
        return total, [self._to_domain(m) for m in models]

    async def update(self, curriculum: CurriculumDomain) -> None:
        existing_curriculum: CurriculumModel | None = await self.session.get(
            CurriculumModel,
            curriculum.id,
            options=[selectinload(CurriculumModel.week_schedules)],
        )

        if not existing_curriculum:
            return None

        existing_curriculum.title = curriculum.title.value
        existing_curriculum.visibility = curriculum.visibility.value
        existing_curriculum.updated_at = curriculum.updated_at

        existing_curriculum.week_schedules.clear()
        for week_schedule in curriculum.week_schedules:
            existing_curriculum.week_schedules.append(
                WeekScheduleModel(  # type: ignore
                    week_number=week_schedule.week_number.value,
                    lessons=week_schedule.lessons.items,
                )
            )
        self.session.add(existing_curriculum)
        await self.session.commit()

    async def delete(self, curriculum_id: str) -> None:
        model: CurriculumModel | None = await self.session.get(
            CurriculumModel, curriculum_id
        )
        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def count_by_owner(self, owner_id: str) -> int:
        stmt: Select[Tuple[int]] = (
            select(func.count())
            .select_from(CurriculumModel)
            .filter(CurriculumModel.user_id == owner_id)
        )
        result: Result[Tuple[int]] = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists_by_id(self, curriculum_id: str) -> bool:
        model: CurriculumModel | None = await self.session.get(
            CurriculumModel, curriculum_id
        )
        return model is not None

    async def find_public_curriculums_by_users(
        self,
        user_ids: List[str],
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[CurriculumDomain]]:
        """특정 사용자들의 공개 커리큘럼 목록 조회"""
        if not user_ids:
            return 0, []

        base_query: Select[Tuple[CurriculumModel]] = (
            select(CurriculumModel)
            .where(
                and_(
                    CurriculumModel.user_id.in_(user_ids),
                    CurriculumModel.visibility == Visibility.PUBLIC.value,
                )
            )
            .options(selectinload(CurriculumModel.week_schedules))
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[CurriculumModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CurriculumModel.created_at.desc())
        )

        result: Result[Tuple[CurriculumModel]] = await self.session.execute(paged_query)
        models: Sequence[CurriculumModel] = result.scalars().all()

        return total_count, [self._to_domain(m) for m in models]
