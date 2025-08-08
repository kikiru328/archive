from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.taxonomy.domain.entity.category import Category
from app.modules.taxonomy.domain.vo.category_name import CategoryName


class ICategoryRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, category: Category) -> None:
        """카테고리 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, category_id: str) -> Optional[Category]:
        """ID로 카테고리 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_name(self, name: CategoryName) -> Optional[Category]:
        """이름으로 카테고리 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_all_active(self) -> List[Category]:
        """활성화된 모든 카테고리를 정렬순으로 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self, page: int = 1, items_per_page: int = 10, include_inactive: bool = False
    ) -> Tuple[int, List[Category]]:
        """모든 카테고리 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_active_status(
        self, is_active: bool, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Category]]:
        """활성화 상태별 카테고리 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_sort_order_range(
        self, min_order: int, max_order: int
    ) -> List[Category]:
        """정렬 순서 범위별 카테고리 조회"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, category: Category) -> None:
        """카테고리 업데이트"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, category_id: str) -> None:
        """카테고리 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_name(self, name: CategoryName) -> bool:
        """같은 이름의 카테고리가 이미 존재하는지 확인"""
        raise NotImplementedError

    @abstractmethod
    async def count_all(self, include_inactive: bool = False) -> int:
        """카테고리 총 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_active(self) -> int:
        """활성화된 카테고리 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def get_max_sort_order(self) -> int:
        """최대 정렬 순서 조회"""
        raise NotImplementedError

    @abstractmethod
    async def reorder_categories(self, category_orders: List[Tuple[str, int]]) -> None:
        """카테고리들의 정렬 순서 일괄 변경"""
        raise NotImplementedError
