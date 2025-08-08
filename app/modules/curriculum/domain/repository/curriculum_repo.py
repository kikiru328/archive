from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.user.domain.vo.role import RoleVO


class ICurriculumRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, curriculum: Curriculum) -> None:
        """커리큘럼 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(
        self,
        curriculum_id: str,
        role: RoleVO,
        owner_id: Optional[str] = None,
    ) -> Optional[Curriculum]:
        """ID로 커리큘럼 조회 (권한 기반)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_owner_id(
        self,
        owner_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Curriculum]]:
        """소유자 ID로 커리큘럼 목록 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_public_curriculums(
        self,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Curriculum]]:
        """공개 커리큘럼 목록 조회"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, curriculum: Curriculum) -> None:
        """커리큘럼 업데이트"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, curriculum_id: str) -> None:
        """커리큘럼 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_owner(self, owner_id: str) -> int:
        """소유자별 커리큘럼 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id(self, curriculum_id: str) -> bool:
        """커리큘럼 존재 여부 확인"""
        raise NotImplementedError

    @abstractmethod
    async def find_public_curriculums_by_users(
        self,
        user_ids: List[str],
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Curriculum]]:
        """특정 사용자들의 공개 커리큘럼 목록 조회"""
        raise NotImplementedError
