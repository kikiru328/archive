from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.social.domain.entity.bookmark import Bookmark


class IBookmarkRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, bookmark: Bookmark) -> None:
        """북마크 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, bookmark_id: str) -> Optional[Bookmark]:
        """ID로 북마크 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> Optional[Bookmark]:
        """커리큘럼과 사용자로 북마크 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Bookmark]]:
        """사용자의 모든 북마크 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, bookmark_id: str) -> None:
        """북마크 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> None:
        """커리큘럼과 사용자로 북마크 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """사용자의 북마크 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> bool:
        """커리큘럼-사용자 북마크 존재 여부 확인"""
        raise NotImplementedError
