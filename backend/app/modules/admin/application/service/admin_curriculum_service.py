from typing import Optional
from app.modules.admin.infrastructure.repository.admin_curriculum_repository import (
    AdminCurriculumRepository,
)
from app.modules.admin.interface.schema.admin_curriculum_schema import (
    AdminCurriculumItem,
    AdminGetCurriculumsPageResponse,
    AdminGetCurriculumResponse,
)


class AdminCurriculumService:
    def __init__(self, repo: AdminCurriculumRepository) -> None:
        self.repo = repo

    async def list_curriculums(
        self, *, page: int, items_per_page: int, owner_id: Optional[str]
    ) -> AdminGetCurriculumsPageResponse:
        total, rows = await self.repo.find_brief_page(
            page=page, items_per_page=items_per_page, owner_id=owner_id
        )
        items = [
            AdminCurriculumItem(
                curriculum_id=r[0], owner_id=r[1], title=r[2], visibility=str(r[3])
            )
            for r in rows
        ]
        return AdminGetCurriculumsPageResponse(
            curriculums=items,
            total_count=total,
            page=page,
            items_per_page=items_per_page,
        )

    async def get_curriculum(self, curriculum_id: str) -> AdminGetCurriculumResponse:
        row = await self.repo.find_brief_by_id(curriculum_id)
        if not row:
            raise ValueError("Curriculum not found")
        return AdminGetCurriculumResponse(
            curriculum_id=row[0], owner_id=row[1], title=row[2], visibility=str(row[3])
        )

    async def change_visibility(
        self, curriculum_id: str, visibility: str
    ) -> AdminGetCurriculumResponse:
        if visibility not in ("PUBLIC", "PRIVATE"):
            raise ValueError("invalid visibility")
        await self.repo.update_visibility(curriculum_id, visibility)
        return await self.get_curriculum(curriculum_id)

    async def delete_curriculum(self, curriculum_id: str) -> None:
        await self.repo.delete_by_id(curriculum_id)
