from typing import List
from ulid import ULID  # type: ignore

from app.modules.curriculum.application.exception import CurriculumNotFoundError
from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.taxonomy.application.dto.tag_dto import (
    AddTagsToCurriculumCommand,
    RemoveTagFromCurriculumCommand,
    AssignCategoryToCurriculumCommand,
    TagDTO,
    CategoryDTO,
    CurriculumTagsDTO,
)
from app.modules.taxonomy.application.exception import (
    TagAccessDeniedError,
    CategoryAccessDeniedError,
    TagLimitExceededError,
    InactiveCategoryAssignmentError,
)
from app.modules.taxonomy.domain.entity.category import Category
from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.service.tag_domain_service import TagDomainService
from app.modules.taxonomy.domain.repository.curriculum_tag_repo import (
    ICurriculumTagRepository,
    ICurriculumCategoryRepository,
)
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.user.domain.vo.role import RoleVO
from app.common.monitoring.metrics import (
    increment_curriculum_tag_assignment,
    increment_curriculum_category_assignment,
)


class CurriculumTagService:
    """커리큘럼-태그/카테고리 애플리케이션 서비스"""

    def __init__(
        self,
        tag_domain_service: TagDomainService,
        curriculum_tag_repo: ICurriculumTagRepository,
        curriculum_category_repo: ICurriculumCategoryRepository,
        curriculum_repo: ICurriculumRepository,
        ulid: ULID = ULID(),
    ) -> None:
        self.tag_domain_service: TagDomainService = tag_domain_service
        self.curriculum_tag_repo: ICurriculumTagRepository = curriculum_tag_repo
        self.curriculum_category_repo: ICurriculumCategoryRepository = (
            curriculum_category_repo
        )
        self.curriculum_repo: ICurriculumRepository = curriculum_repo
        self.ulid: ULID = ulid

    async def add_tags_to_curriculum(
        self,
        command: AddTagsToCurriculumCommand,
        role: RoleVO = RoleVO.USER,
    ) -> List[TagDTO]:
        """커리큘럼에 태그 추가"""
        # 커리큘럼 존재 및 권한 확인
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=command.user_id if role != RoleVO.ADMIN else None,
        )
        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        # 권한 확인
        if role != RoleVO.ADMIN and curriculum.owner_id != command.user_id:
            raise TagAccessDeniedError("You can only add tags to your own curriculum")

        # 태그 개수 제한 확인
        if not await self.tag_domain_service.validate_curriculum_tag_limit(
            command.curriculum_id, max_tags=10
        ):
            raise TagLimitExceededError("Cannot add more than 10 tags to a curriculum")

        # 태그 추가
        added_tags: List[Tag] = await self.tag_domain_service.add_tags_to_curriculum(
            curriculum_id=command.curriculum_id,
            tag_names=command.tag_names,
            user_id=command.user_id,
        )
        for _ in added_tags:
            increment_curriculum_tag_assignment()
        return [TagDTO.from_domain(tag) for tag in added_tags]

    async def remove_tag_from_curriculum(
        self,
        command: RemoveTagFromCurriculumCommand,
        user_id: str,
        role: RoleVO = RoleVO.USER,
    ) -> None:
        """커리큘럼에서 태그 제거"""
        # 커리큘럼 존재 및 권한 확인
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=user_id if role != RoleVO.ADMIN else None,
        )
        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        # 권한 확인
        if role != RoleVO.ADMIN and curriculum.owner_id != user_id:
            raise TagAccessDeniedError(
                "You can only remove tags from your own curriculum"
            )

        await self.tag_domain_service.remove_tag_from_curriculum(
            curriculum_id=command.curriculum_id,
            tag_name=command.tag_name,
        )

    async def assign_category_to_curriculum(
        self,
        command: AssignCategoryToCurriculumCommand,
        role: RoleVO = RoleVO.USER,
    ) -> CategoryDTO:
        """커리큘럼에 카테고리 할당"""
        # 커리큘럼 존재 및 권한 확인
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=command.user_id if role != RoleVO.ADMIN else None,
        )
        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        # 권한 확인
        if role != RoleVO.ADMIN and curriculum.owner_id != command.user_id:
            raise CategoryAccessDeniedError(
                "You can only assign category to your own curriculum"
            )

        # 카테고리 할당 유효성 검증
        if not await self.tag_domain_service.validate_category_assignment(
            command.category_id
        ):
            raise InactiveCategoryAssignmentError("Cannot assign inactive category")

        category: Category = (
            await self.tag_domain_service.assign_category_to_curriculum(
                curriculum_id=command.curriculum_id,
                category_id=command.category_id,
                user_id=command.user_id,
            )
        )
        increment_curriculum_category_assignment()
        return CategoryDTO.from_domain(category)

    async def remove_category_from_curriculum(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO = RoleVO.USER,
    ) -> None:
        """커리큘럼에서 카테고리 제거"""
        # 커리큘럼 존재 및 권한 확인
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id if role != RoleVO.ADMIN else None,
        )
        if not curriculum:
            raise CurriculumNotFoundError(f"Curriculum {curriculum_id} not found")

        # 권한 확인
        if role != RoleVO.ADMIN and curriculum.owner_id != user_id:
            raise CategoryAccessDeniedError(
                "You can only remove category from your own curriculum"
            )

        await self.tag_domain_service.remove_category_from_curriculum(curriculum_id)

    async def get_curriculum_tags_and_category(
        self, curriculum_id: str, user_id: str, role: RoleVO = RoleVO.USER
    ) -> CurriculumTagsDTO:
        """커리큘럼의 태그와 카테고리 조회"""
        # 커리큘럼 존재 확인 (공개 커리큘럼도 조회 가능)
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id if role != RoleVO.ADMIN else None,
        )
        if not curriculum:
            raise CurriculumNotFoundError(f"Curriculum {curriculum_id} not found")

        # 태그 조회
        tags = await self.curriculum_tag_repo.find_tags_by_curriculum(curriculum_id)

        # 카테고리 조회
        category: Category | None = (
            await self.curriculum_category_repo.find_category_by_curriculum(
                curriculum_id
            )
        )

        return CurriculumTagsDTO.from_domain(
            curriculum_id=curriculum_id,
            tags=tags,
            category=category,
        )

    async def find_curriculums_by_tags(
        self,
        tag_names: List[str],
        page: int = 1,
        items_per_page: int = 10,
    ) -> tuple[int, List[str]]:
        """태그로 커리큘럼 검색"""
        return await self.curriculum_tag_repo.find_curriculums_by_tag_names(
            tag_names, page, items_per_page
        )

    async def find_curriculums_by_category(
        self,
        category_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> tuple[int, List[str]]:
        """카테고리로 커리큘럼 검색"""
        return await self.curriculum_category_repo.find_curriculums_by_category(
            category_id, page, items_per_page
        )

    async def get_user_tagged_curriculums(
        self,
        user_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> tuple[int, List[str]]:
        """사용자가 태그를 추가한 커리큘럼 목록 조회"""
        total_count, curriculum_tags = await self.curriculum_tag_repo.find_by_user(
            user_id, page, items_per_page
        )
        curriculum_ids = [ct.curriculum_id for ct in curriculum_tags]
        return total_count, curriculum_ids

    async def get_user_categorized_curriculums(
        self,
        user_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> tuple[int, List[str]]:
        """사용자가 카테고리를 할당한 커리큘럼 목록 조회"""
        total_count, curriculum_categories = (
            await self.curriculum_category_repo.find_by_user(
                user_id, page, items_per_page
            )
        )
        curriculum_ids: List[str] = [cc.curriculum_id for cc in curriculum_categories]
        return total_count, curriculum_ids
