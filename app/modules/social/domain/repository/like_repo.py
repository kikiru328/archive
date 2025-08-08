from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.social.domain.entity.like import Like


class ILikeRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, like: Like) -> None:
        """좋아요 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, like_id: str) -> Optional[Like]:
        """ID로 좋아요 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> Optional[Like]:
        """커리큘럼과 사용자로 좋아요 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum(
        self, curriculum_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Like]]:
        """커리큘럼의 모든 좋아요 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Like]]:
        """사용자의 모든 좋아요 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, like_id: str) -> None:
        """좋아요 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> None:
        """커리큘럼과 사용자로 좋아요 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 좋아요 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """사용자의 좋아요 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> bool:
        """커리큘럼-사용자 좋아요 존재 여부 확인"""
        raise NotImplementedError
