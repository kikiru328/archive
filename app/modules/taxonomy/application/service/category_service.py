from datetime import datetime
from typing import List, Optional
from ulid import ULID  # type: ignore
from app.core.auth import Role
from app.modules.taxonomy.application.dto.tag_dto import (
    CreateCategoryCommand,
    UpdateCategoryCommand,
    CategoryQuery,
    CategoryDTO,
    CategoryPageDTO,
    CategoryStatisticsDTO,
)
from app.modules.taxonomy.application.exception import (
    CategoryNotFoundError,
    DuplicateCategoryError,
    CategoryAccessDeniedError,
    InvalidCategoryNameError,
    InvalidColorFormatError,
    CategoryInUseError,
)
from app.modules.taxonomy.domain.entity.category import Category
from app.modules.taxonomy.domain.repository.category_repo import ICategoryRepository
from app.modules.taxonomy.domain.repository.curriculum_tag_repo import (
    ICurriculumCategoryRepository,
)
from app.modules.taxonomy.domain.vo.category_name import CategoryName
from app.modules.taxonomy.domain.vo.tag_color import TagColor
from app.modules.taxonomy.domain.service.tag_domain_service import TagDomainService
from app.modules.user.domain.vo.role import RoleVO


class CategoryService:
    """카테고리 애플리케이션 서비스"""

    def __init__(
        self,
        category_repo: ICategoryRepository,
        curriculum_category_repo: ICurriculumCategoryRepository,
        tag_domain_service: TagDomainService,
        ulid: ULID = ULID(),
    ) -> None:
        self.category_repo: ICategoryRepository = category_repo
        self.curriculum_category_repo: ICurriculumCategoryRepository = (
            curriculum_category_repo
        )
        self.tag_domain_service = tag_domain_service
        self.ulid: ULID = ulid

    async def create_category(
        self,
        command: CreateCategoryCommand,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
        created_at: Optional[datetime] = None,
    ) -> CategoryDTO:
        """카테고리 생성 (관리자만)"""
        if role != RoleVO.ADMIN:
            raise CategoryAccessDeniedError("Only administrators can create categories")

        try:
            # 도메인 서비스를 통한 유효성 검증
            await self.tag_domain_service.validate_category_creation(command.name)

            # 다음 정렬 순서 설정
            if command.sort_order == 0:
                sort_order: int = await self.tag_domain_service.get_next_sort_order()
            else:
                sort_order = command.sort_order

            # 카테고리 생성
            category: Category = await self.tag_domain_service.create_category(
                category_id=self.ulid.generate(),
                name=command.name,
                description=command.description,
                color=command.color,
                icon=command.icon,
                sort_order=sort_order,
                created_at=created_at,
            )

            await self.category_repo.save(category)
            return CategoryDTO.from_domain(category)

        except ValueError as e:
            if "already exists" in str(e):
                raise DuplicateCategoryError(str(e))
            elif "색상" in str(e) or "#" in str(e):
                raise InvalidColorFormatError(str(e))
            raise InvalidCategoryNameError(str(e))

    async def get_category_by_id(
        self,
        category_id: str,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> CategoryDTO:
        """ID로 카테고리 조회"""
        category: Category | None = await self.category_repo.find_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")

        # 사용 횟수 조회
        usage_count: int = await self.curriculum_category_repo.count_by_category(
            category_id
        )
        return CategoryDTO.from_domain(category, usage_count)

    async def get_active_categories(self) -> List[CategoryDTO]:
        """활성화된 카테고리 목록 조회"""
        categories: List[Category] = await self.category_repo.find_all_active()

        # 각 카테고리의 사용 횟수 조회
        category_dtos = []
        for category in categories:
            usage_count = await self.curriculum_category_repo.count_by_category(
                category.id
            )
            category_dtos.append(CategoryDTO.from_domain(category, usage_count))

        return category_dtos

    async def get_categories(
        self,
        query: CategoryQuery,
    ) -> CategoryPageDTO:
        """카테고리 목록 조회"""
        total_count, categories = await self.category_repo.find_all(
            page=query.page,
            items_per_page=query.items_per_page,
            include_inactive=query.include_inactive,
        )

        # 각 카테고리의 사용 횟수 조회
        usage_counts = []
        for category in categories:
            usage_count: int = await self.curriculum_category_repo.count_by_category(
                category.id
            )
            usage_counts.append(usage_count)

        return CategoryPageDTO.from_domain(
            total_count=total_count,
            page=query.page,
            items_per_page=query.items_per_page,
            categories=categories,
            usage_counts=usage_counts,
        )

    async def update_category(
        self,
        command: UpdateCategoryCommand,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> CategoryDTO:
        """카테고리 수정 (관리자만)"""
        if role != RoleVO.ADMIN:
            raise CategoryAccessDeniedError("Only administrators can modify categories")

        category: Category | None = await self.category_repo.find_by_id(
            command.category_id
        )
        if not category:
            raise CategoryNotFoundError(f"Category {command.category_id} not found")

        try:
            # 이름 변경
            if command.name:
                new_name: CategoryName = (
                    await self.tag_domain_service.validate_category_creation(
                        command.name, category.id
                    )
                )
                category.change_name(new_name)

            # 기타 속성 변경
            if command.description is not None:
                category.change_description(command.description)

            if command.color:

                category.change_color(TagColor(command.color))

            if command.icon is not None:
                category.change_icon(command.icon)

            if command.sort_order is not None:
                category.change_sort_order(command.sort_order)

            if command.is_active is not None:
                if command.is_active:
                    category.activate()
                else:
                    category.deactivate()

            await self.category_repo.update(category)

            # 사용 횟수 포함하여 반환
            usage_count: int = await self.curriculum_category_repo.count_by_category(
                category.id
            )
            return CategoryDTO.from_domain(category, usage_count)

        except ValueError as e:
            if "already exists" in str(e):
                raise DuplicateCategoryError(str(e))
            elif "색상" in str(e) or "#" in str(e):
                raise InvalidColorFormatError(str(e))
            raise InvalidCategoryNameError(str(e))

    async def delete_category(
        self,
        category_id: str,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> None:
        """카테고리 삭제 (관리자만)"""
        if role != RoleVO.ADMIN:
            raise CategoryAccessDeniedError("Only administrators can delete categories")

        category: Category | None = await self.category_repo.find_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")

        # 삭제 가능 여부 확인
        if not await self.tag_domain_service.can_delete_category(category_id):
            curriculum_count: int = (
                await self.curriculum_category_repo.count_by_category(category_id)
            )
            raise CategoryInUseError(
                f"Category is used by {curriculum_count} curriculums"
            )

        await self.category_repo.delete(category_id)

    async def activate_category(
        self,
        category_id: str,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> CategoryDTO:
        """카테고리 활성화 (관리자만)"""
        if role != RoleVO.ADMIN:
            raise CategoryAccessDeniedError(
                "Only administrators can activate categories"
            )

        category: Category | None = await self.category_repo.find_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")

        category.activate()
        await self.category_repo.update(category)

        usage_count: int = await self.curriculum_category_repo.count_by_category(
            category_id
        )
        return CategoryDTO.from_domain(category, usage_count)

    async def deactivate_category(
        self,
        category_id: str,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> CategoryDTO:
        """카테고리 비활성화 (관리자만)"""
        if role != RoleVO.ADMIN:
            raise CategoryAccessDeniedError(
                "Only administrators can deactivate categories"
            )

        category: Category | None = await self.category_repo.find_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")

        category.deactivate()
        await self.category_repo.update(category)

        usage_count: int = await self.curriculum_category_repo.count_by_category(
            category_id
        )
        return CategoryDTO.from_domain(category, usage_count)

    async def reorder_categories(
        self,
        category_orders: List[tuple[str, int]],
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> None:
        """카테고리 순서 재정렬 (관리자만)"""
        if role != RoleVO.ADMIN:
            raise CategoryAccessDeniedError(
                "Only administrators can reorder categories"
            )

        await self.category_repo.reorder_categories(category_orders)

    async def get_category_statistics(self) -> CategoryStatisticsDTO:
        """카테고리 통계 정보 조회"""
        stats = await self.tag_domain_service.get_category_statistics()
        return CategoryStatisticsDTO(
            total_categories=stats["total_categories"],
            active_categories=stats["active_categories"],
            inactive_categories=stats["inactive_categories"],
        )
