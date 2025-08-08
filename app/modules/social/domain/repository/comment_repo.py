from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.social.domain.entity.comment import Comment


class ICommentRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, comment: Comment) -> None:
        """댓글 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, comment_id: str) -> Optional[Comment]:
        """ID로 댓글 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum(
        self, curriculum_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Comment]]:
        """커리큘럼의 모든 댓글 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Comment]]:
        """사용자의 모든 댓글 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, comment: Comment) -> None:
        """댓글 업데이트"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, comment_id: str) -> None:
        """댓글 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 댓글 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """사용자의 댓글 수 조회"""
        raise NotImplementedError
