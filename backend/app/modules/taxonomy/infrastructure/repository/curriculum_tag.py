from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID  # type: ignore

from app.modules.taxonomy.domain.entity.curriculum_tag import (
    CurriculumTag,
    CurriculumCategory,
)
from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.entity.category import Category
from app.modules.taxonomy.domain.repository.curriculum_tag_repo import (
    ICurriculumTagRepository,
    ICurriculumCategoryRepository,
)
from app.modules.taxonomy.domain.vo.tag_name import TagName
from app.modules.taxonomy.domain.vo.category_name import CategoryName
from app.modules.taxonomy.domain.vo.tag_color import TagColor
from app.modules.taxonomy.infrastructure.db_model.curriculum_tag import (
    CurriculumTagModel,
    CurriculumCategoryModel,
)
from app.modules.taxonomy.infrastructure.db_model.tag import TagModel
from app.modules.taxonomy.infrastructure.db_model.category import CategoryModel


class CurriculumTagRepository(ICurriculumTagRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _map_to_entity(self, curriculum_tag_model: CurriculumTagModel) -> CurriculumTag:
        return CurriculumTag(
            id=curriculum_tag_model.id,
            curriculum_id=curriculum_tag_model.curriculum_id,
            tag_id=curriculum_tag_model.tag_id,
            added_by=curriculum_tag_model.added_by,
            created_at=curriculum_tag_model.created_at,
        )

    def _map_tag_to_entity(self, tag_model: TagModel) -> Tag:
        return Tag(
            id=tag_model.id,
            name=TagName(tag_model.name),
            usage_count=tag_model.usage_count,
            created_by=tag_model.created_by,
            created_at=tag_model.created_at,
            updated_at=tag_model.updated_at,
        )

    async def save(self, curriculum_tag: CurriculumTag) -> None:
        """커리큘럼-태그 연결 저장"""
        new_curriculum_tag = CurriculumTagModel(  # type: ignore
            id=curriculum_tag.id,
            curriculum_id=curriculum_tag.curriculum_id,
            tag_id=curriculum_tag.tag_id,
            added_by=curriculum_tag.added_by,
            created_at=curriculum_tag.created_at,
        )
        self.session.add(new_curriculum_tag)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, curriculum_tag_id: str) -> Optional[CurriculumTag]:
        """ID로 커리큘럼-태그 연결 조회"""
        query = select(CurriculumTagModel).where(
            CurriculumTagModel.id == curriculum_tag_id
        )
        result = await self.session.execute(query)
        curriculum_tag_model = result.scalar_one_or_none()

        if not curriculum_tag_model:
            return None

        return self._map_to_entity(curriculum_tag_model)

    async def find_by_curriculum_and_tag(
        self, curriculum_id: str, tag_id: str
    ) -> Optional[CurriculumTag]:
        """커리큘럼과 태그로 연결 조회"""
        query = select(CurriculumTagModel).where(
            CurriculumTagModel.curriculum_id == curriculum_id,
            CurriculumTagModel.tag_id == tag_id,
        )
        result = await self.session.execute(query)
        curriculum_tag_model = result.scalar_one_or_none()

        if not curriculum_tag_model:
            return None

        return self._map_to_entity(curriculum_tag_model)

    async def find_tags_by_curriculum(self, curriculum_id: str) -> List[Tag]:
        """커리큘럼에 연결된 모든 태그 조회"""
        query = (
            select(TagModel)
            .join(CurriculumTagModel)
            .where(CurriculumTagModel.curriculum_id == curriculum_id)
            .order_by(TagModel.name.asc())
        )

        result = await self.session.execute(query)
        tag_models = result.scalars().all()

        return [self._map_tag_to_entity(model) for model in tag_models]

    async def find_curriculums_by_tag(
        self, tag_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """특정 태그가 연결된 커리큘럼 ID 목록 조회"""
        base_query = select(CurriculumTagModel.curriculum_id).where(
            CurriculumTagModel.tag_id == tag_id
        )

        # 총 개수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset = (page - 1) * items_per_page
        paged_query = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CurriculumTagModel.created_at.desc())
        )

        result = await self.session.execute(paged_query)
        curriculum_ids = result.scalars().all()

        return total_count, list(curriculum_ids)

    async def find_curriculums_by_tag_names(
        self, tag_names: List[str], page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """여러 태그 이름으로 커리큘럼 검색 (교집합)"""
        # 태그 이름들로 태그 ID들 찾기
        tag_query = select(TagModel.id).where(TagModel.name.in_(tag_names))
        tag_result = await self.session.execute(tag_query)
        tag_ids = tag_result.scalars().all()

        if not tag_ids:
            return 0, []

        # 태그들이 모두 연결된 커리큘럼 찾기 (교집합)
        base_query = (
            select(CurriculumTagModel.curriculum_id)
            .where(CurriculumTagModel.tag_id.in_(tag_ids))
            .group_by(CurriculumTagModel.curriculum_id)
            .having(func.count(CurriculumTagModel.tag_id) == len(tag_ids))
        )

        # 총 개수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset = (page - 1) * items_per_page
        paged_query = base_query.limit(items_per_page).offset(offset)

        result = await self.session.execute(paged_query)
        curriculum_ids = result.scalars().all()

        return total_count, list(curriculum_ids)

    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[CurriculumTag]]:
        """사용자가 추가한 태그 연결 조회"""
        base_query = select(CurriculumTagModel).where(
            CurriculumTagModel.added_by == user_id
        )

        # 총 개수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset = (page - 1) * items_per_page
        paged_query = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CurriculumTagModel.created_at.desc())
        )

        result = await self.session.execute(paged_query)
        curriculum_tag_models = result.scalars().all()

        curriculum_tags = [
            self._map_to_entity(model) for model in curriculum_tag_models
        ]
        return total_count, curriculum_tags

    async def delete(self, curriculum_tag_id: str) -> None:
        """커리큘럼-태그 연결 삭제"""
        query = delete(CurriculumTagModel).where(
            CurriculumTagModel.id == curriculum_tag_id
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_by_curriculum_and_tag(
        self, curriculum_id: str, tag_id: str
    ) -> None:
        """커리큘럼과 태그로 연결 삭제"""
        query = delete(CurriculumTagModel).where(
            CurriculumTagModel.curriculum_id == curriculum_id,
            CurriculumTagModel.tag_id == tag_id,
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_all_by_curriculum(self, curriculum_id: str) -> None:
        """커리큘럼의 모든 태그 연결 삭제"""
        query = delete(CurriculumTagModel).where(
            CurriculumTagModel.curriculum_id == curriculum_id
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_all_by_tag(self, tag_id: str) -> None:
        """태그의 모든 커리큘럼 연결 삭제"""
        query = delete(CurriculumTagModel).where(CurriculumTagModel.tag_id == tag_id)
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 태그 수 조회"""
        query = (
            select(func.count())
            .select_from(CurriculumTagModel)
            .where(CurriculumTagModel.curriculum_id == curriculum_id)
        )
        return await self.session.scalar(query) or 0

    async def count_by_tag(self, tag_id: str) -> int:
        """특정 태그를 사용하는 커리큘럼 수"""
        query = (
            select(func.count())
            .select_from(CurriculumTagModel)
            .where(CurriculumTagModel.tag_id == tag_id)
        )
        return await self.session.scalar(query) or 0

    async def exists_by_curriculum_and_tag(
        self, curriculum_id: str, tag_id: str
    ) -> bool:
        """커리큘럼-태그 연결 존재 여부 확인"""
        query = select(CurriculumTagModel).where(
            CurriculumTagModel.curriculum_id == curriculum_id,
            CurriculumTagModel.tag_id == tag_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None


class CurriculumCategoryRepository(ICurriculumCategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _map_to_entity(
        self, curriculum_category_model: CurriculumCategoryModel
    ) -> CurriculumCategory:
        return CurriculumCategory(
            id=curriculum_category_model.id,
            curriculum_id=curriculum_category_model.curriculum_id,
            category_id=curriculum_category_model.category_id,
            assigned_by=curriculum_category_model.assigned_by,
            created_at=curriculum_category_model.created_at,
        )

    def _map_category_to_entity(self, category_model: CategoryModel) -> Category:
        return Category(
            id=category_model.id,
            name=CategoryName(category_model.name),
            description=category_model.description,
            color=TagColor(category_model.color),
            icon=category_model.icon,
            sort_order=category_model.sort_order,
            is_active=category_model.is_active,
            created_at=category_model.created_at,
            updated_at=category_model.updated_at,
        )

    async def save(self, curriculum_category: CurriculumCategory) -> None:
        """커리큘럼-카테고리 연결 저장"""
        new_curriculum_category = CurriculumCategoryModel(  # type: ignore
            id=curriculum_category.id,
            curriculum_id=curriculum_category.curriculum_id,
            category_id=curriculum_category.category_id,
            assigned_by=curriculum_category.assigned_by,
            created_at=curriculum_category.created_at,
        )
        self.session.add(new_curriculum_category)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(
        self, curriculum_category_id: str
    ) -> Optional[CurriculumCategory]:
        """ID로 커리큘럼-카테고리 연결 조회"""
        query = select(CurriculumCategoryModel).where(
            CurriculumCategoryModel.id == curriculum_category_id
        )
        result = await self.session.execute(query)
        curriculum_category_model = result.scalar_one_or_none()

        if not curriculum_category_model:
            return None

        return self._map_to_entity(curriculum_category_model)

    async def find_by_curriculum(
        self, curriculum_id: str
    ) -> Optional[CurriculumCategory]:
        """커리큘럼의 카테고리 연결 조회 (1:1 관계)"""
        query = select(CurriculumCategoryModel).where(
            CurriculumCategoryModel.curriculum_id == curriculum_id
        )
        result = await self.session.execute(query)
        curriculum_category_model = result.scalar_one_or_none()

        if not curriculum_category_model:
            return None

        return self._map_to_entity(curriculum_category_model)

    async def find_category_by_curriculum(
        self, curriculum_id: str
    ) -> Optional[Category]:
        """커리큘럼에 연결된 카테고리 조회"""
        query = (
            select(CategoryModel)
            .join(CurriculumCategoryModel)
            .where(CurriculumCategoryModel.curriculum_id == curriculum_id)
        )

        result = await self.session.execute(query)
        category_model = result.scalar_one_or_none()

        if not category_model:
            return None

        return self._map_category_to_entity(category_model)

    async def find_curriculums_by_category(
        self, category_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """특정 카테고리의 커리큘럼 ID 목록 조회"""
        base_query = select(CurriculumCategoryModel.curriculum_id).where(
            CurriculumCategoryModel.category_id == category_id
        )

        # 총 개수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset = (page - 1) * items_per_page
        paged_query = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CurriculumCategoryModel.created_at.desc())
        )

        result = await self.session.execute(paged_query)
        curriculum_ids = result.scalars().all()

        return total_count, list(curriculum_ids)

    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[CurriculumCategory]]:
        """사용자가 할당한 카테고리 연결 조회"""
        base_query = select(CurriculumCategoryModel).where(
            CurriculumCategoryModel.assigned_by == user_id
        )

        # 총 개수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset = (page - 1) * items_per_page
        paged_query = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CurriculumCategoryModel.created_at.desc())
        )

        result = await self.session.execute(paged_query)
        curriculum_category_models = result.scalars().all()

        curriculum_categories = [
            self._map_to_entity(model) for model in curriculum_category_models
        ]
        return total_count, curriculum_categories

    async def update_curriculum_category(
        self, curriculum_id: str, new_category_id: str, assigned_by: str
    ) -> None:
        """커리큘럼의 카테고리 변경 (기존 삭제 후 새로 생성)"""
        # 기존 카테고리 삭제
        await self.delete_by_curriculum(curriculum_id)

        # 새 카테고리 할당
        new_curriculum_category = CurriculumCategory(
            id=ULID().generate(),
            curriculum_id=curriculum_id,
            category_id=new_category_id,
            assigned_by=assigned_by,
            created_at=datetime.now(timezone.utc),
        )
        await self.save(new_curriculum_category)

    async def delete(self, curriculum_category_id: str) -> None:
        """커리큘럼-카테고리 연결 삭제"""
        query = delete(CurriculumCategoryModel).where(
            CurriculumCategoryModel.id == curriculum_category_id
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_by_curriculum(self, curriculum_id: str) -> None:
        """커리큘럼의 카테고리 연결 삭제"""
        query = delete(CurriculumCategoryModel).where(
            CurriculumCategoryModel.curriculum_id == curriculum_id
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_all_by_category(self, category_id: str) -> None:
        """카테고리의 모든 커리큘럼 연결 삭제"""
        query = delete(CurriculumCategoryModel).where(
            CurriculumCategoryModel.category_id == category_id
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def count_by_category(self, category_id: str) -> int:
        """특정 카테고리를 사용하는 커리큘럼 수"""
        query = (
            select(func.count())
            .select_from(CurriculumCategoryModel)
            .where(CurriculumCategoryModel.category_id == category_id)
        )
        return await self.session.scalar(query) or 0

    async def exists_by_curriculum(self, curriculum_id: str) -> bool:
        """커리큘럼에 카테고리가 할당되어 있는지 확인"""
        query = select(CurriculumCategoryModel).where(
            CurriculumCategoryModel.curriculum_id == curriculum_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
