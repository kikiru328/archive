from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, func, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.taxonomy.domain.entity.category import Category
from app.modules.taxonomy.domain.repository.category_repo import ICategoryRepository
from app.modules.taxonomy.domain.vo.category_name import CategoryName
from app.modules.taxonomy.domain.vo.tag_color import TagColor
from app.modules.taxonomy.infrastructure.db_model.category import CategoryModel


class CategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, category_model: CategoryModel) -> Category:
        """DB Model → Domain Entity 변환"""
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

    async def save(self, category: Category) -> None:
        """카테고리 저장"""
        new_category = CategoryModel(  # type: ignore
            id=category.id,
            name=category.name.value,
            description=category.description,
            color=category.color.value,
            icon=category.icon,
            sort_order=category.sort_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
        self.session.add(new_category)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, category_id: str) -> Optional[Category]:
        """ID로 카테고리 조회"""
        query: Select[Tuple[CategoryModel]] = select(CategoryModel).where(
            CategoryModel.id == category_id
        )
        result: Result[Tuple[CategoryModel]] = await self.session.execute(query)
        category_model: CategoryModel | None = result.scalar_one_or_none()

        if not category_model:
            return None

        return self._to_domain(category_model)

    async def find_by_name(self, name: CategoryName) -> Optional[Category]:
        """이름으로 카테고리 조회"""
        query: Select[Tuple[CategoryModel]] = select(CategoryModel).where(
            CategoryModel.name == name.value
        )
        result: Result[Tuple[CategoryModel]] = await self.session.execute(query)
        category_model: CategoryModel | None = result.scalar_one_or_none()

        if not category_model:
            return None

        return self._to_domain(category_model)

    async def find_all_active(self) -> List[Category]:
        """활성화된 모든 카테고리를 정렬순으로 조회"""
        query: Select[Tuple[CategoryModel]] = (
            select(CategoryModel)
            .where(CategoryModel.is_active)
            .order_by(CategoryModel.sort_order.asc(), CategoryModel.name.asc())
        )

        result: Result[Tuple[CategoryModel]] = await self.session.execute(query)
        category_models: Sequence[CategoryModel] = result.scalars().all()

        return [self._to_domain(model) for model in category_models]

    async def find_all(
        self, page: int = 1, items_per_page: int = 10, include_inactive: bool = False
    ) -> Tuple[int, List[Category]]:
        """모든 카테고리 조회 (페이징)"""
        base_query: Select[Tuple[CategoryModel]] = select(CategoryModel)

        if not include_inactive:
            base_query = base_query.where(CategoryModel.is_active)

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[CategoryModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CategoryModel.sort_order.asc(), CategoryModel.name.asc())
        )

        result: Result[Tuple[CategoryModel]] = await self.session.execute(paged_query)
        category_models: Sequence[CategoryModel] = result.scalars().all()

        categories: List[Category] = [
            self._to_domain(model) for model in category_models
        ]
        return total_count, categories

    async def find_by_active_status(
        self, is_active: bool, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Category]]:
        """활성화 상태별 카테고리 조회"""
        base_query: Select[Tuple[CategoryModel]] = select(CategoryModel).where(
            CategoryModel.is_active == is_active
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[CategoryModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CategoryModel.sort_order.asc(), CategoryModel.name.asc())
        )

        result: Result[Tuple[CategoryModel]] = await self.session.execute(paged_query)
        category_models: Sequence[CategoryModel] = result.scalars().all()

        categories: List[Category] = [
            self._to_domain(model) for model in category_models
        ]
        return total_count, categories

    async def find_by_sort_order_range(
        self, min_order: int, max_order: int
    ) -> List[Category]:
        """정렬 순서 범위별 카테고리 조회"""
        query: Select[Tuple[CategoryModel]] = (
            select(CategoryModel)
            .where(CategoryModel.sort_order.between(min_order, max_order))
            .order_by(CategoryModel.sort_order.asc())
        )

        result: Result[Tuple[CategoryModel]] = await self.session.execute(query)
        category_models: Sequence[CategoryModel] = result.scalars().all()

        return [self._to_domain(model) for model in category_models]

    async def update(self, category: Category) -> None:
        """카테고리 업데이트"""
        existing_category: CategoryModel | None = await self.session.get(
            CategoryModel, category.id
        )
        if not existing_category:
            raise ValueError(f"Category {category.id} not found")

        existing_category.name = category.name.value
        existing_category.description = category.description
        existing_category.color = category.color.value
        existing_category.icon = category.icon
        existing_category.sort_order = category.sort_order
        existing_category.is_active = category.is_active
        existing_category.updated_at = category.updated_at

        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete(self, category_id: str) -> None:
        """카테고리 삭제"""
        query = delete(CategoryModel).where(CategoryModel.id == category_id)
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def exists_by_name(self, name: CategoryName) -> bool:
        """같은 이름의 카테고리가 이미 존재하는지 확인"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(CategoryModel)
            .where(CategoryModel.name == name.value)
        )
        count: int = await self.session.scalar(query) or 0
        return count > 0

    async def count_all(self, include_inactive: bool = False) -> int:
        """카테고리 총 개수 조회"""
        query: Select[Tuple[int]] = select(func.count()).select_from(CategoryModel)

        if not include_inactive:
            query = query.where(CategoryModel.is_active)

        return await self.session.scalar(query) or 0

    async def count_active(self) -> int:
        """활성화된 카테고리 개수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(CategoryModel)
            .where(CategoryModel.is_active)
        )
        return await self.session.scalar(query) or 0

    async def get_max_sort_order(self) -> int:
        """최대 정렬 순서 조회"""
        query: Select[Tuple[int]] = select(func.max(CategoryModel.sort_order))
        result: int | None = await self.session.scalar(query)
        return result or 0

    async def reorder_categories(self, category_orders: List[Tuple[str, int]]) -> None:
        """카테고리들의 정렬 순서 일괄 변경"""
        for category_id, sort_order in category_orders:
            query = (
                update(CategoryModel)
                .where(CategoryModel.id == category_id)
                .values(sort_order=sort_order)
            )
            await self.session.execute(query)

        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise
