from typing import List, Tuple, Optional
from sqlalchemy import select, func, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.curriculum.infrastructure.db_model.curriculum import CurriculumModel


class AdminCurriculumRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_brief_page(
        self, *, page: int, items_per_page: int, owner_id: Optional[str]
    ) -> Tuple[int, List[tuple]]:
        offset = (page - 1) * items_per_page

        # total
        if owner_id:
            total_stmt = (
                select(func.count())
                .select_from(CurriculumModel)
                .where(CurriculumModel.user_id == owner_id)
            )
        else:
            total_stmt = select(func.count()).select_from(CurriculumModel)

        total = int((await self.session.scalar(total_stmt)) or 0)

        # rows (관계 없음, 컬럼만)
        stmt = (
            select(
                CurriculumModel.id,
                CurriculumModel.user_id,
                CurriculumModel.title,
                CurriculumModel.visibility,
            ).where(CurriculumModel.user_id == owner_id)
            if owner_id
            else select(
                CurriculumModel.id,
                CurriculumModel.user_id,
                CurriculumModel.title,
                CurriculumModel.visibility,
            )
        )

        stmt = (
            stmt.order_by(CurriculumModel.created_at.desc(), CurriculumModel.id.desc())
            .offset(offset)
            .limit(items_per_page)
        )

        rows = (await self.session.execute(stmt)).all()
        # rows: List[Row]; 각 Row는 (id, owner_id, title, visibility)
        return total, [(r[0], r[1], r[2], r[3]) for r in rows]

    async def find_brief_by_id(self, curriculum_id: str) -> Optional[tuple]:
        stmt = select(
            CurriculumModel.id,
            CurriculumModel.user_id,
            CurriculumModel.title,
            CurriculumModel.visibility,
        ).where(CurriculumModel.id == curriculum_id)
        row = (await self.session.execute(stmt)).first()
        return (row[0], row[1], row[2], row[3]) if row else None

    async def update_visibility(self, curriculum_id: str, visibility: str) -> None:
        stmt = (
            sa_update(CurriculumModel)
            .where(CurriculumModel.id == curriculum_id)
            .values(visibility=visibility)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_by_id(self, curriculum_id: str) -> None:
        stmt = sa_delete(CurriculumModel).where(CurriculumModel.id == curriculum_id)
        await self.session.execute(stmt)
        await self.session.commit()
