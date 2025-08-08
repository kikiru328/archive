from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.social.domain.entity.follow import Follow


class IFollowRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, follow: Follow) -> None:
        """팔로우 관계 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, follow_id: str) -> Optional[Follow]:
        """ID로 팔로우 관계 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_follower_and_followee(
        self, follower_id: str, followee_id: str
    ) -> Optional[Follow]:
        """팔로워와 팔로위로 팔로우 관계 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_followers(
        self, followee_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Follow]]:
        """특정 사용자의 팔로워 목록 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_followees(
        self, follower_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Follow]]:
        """특정 사용자가 팔로우하는 사람들 목록 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, follow_id: str) -> None:
        """팔로우 관계 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_follower_and_followee(
        self, follower_id: str, followee_id: str
    ) -> None:
        """팔로워와 팔로위로 팔로우 관계 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_followers(self, followee_id: str) -> int:
        """특정 사용자의 팔로워 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_followees(self, follower_id: str) -> int:
        """특정 사용자가 팔로우하는 사람 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def exists_follow(self, follower_id: str, followee_id: str) -> bool:
        """팔로우 관계 존재 여부 확인"""
        raise NotImplementedError

    @abstractmethod
    async def delete_all_by_user(self, user_id: str) -> None:
        """특정 사용자와 관련된 모든 팔로우 관계 삭제 (계정 삭제시)"""
        raise NotImplementedError

    @abstractmethod
    async def get_mutual_followers(
        self, user1_id: str, user2_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """두 사용자의 공통 팔로워 목록 조회"""
        raise NotImplementedError

    @abstractmethod
    async def get_follow_suggestions(self, user_id: str, limit: int = 10) -> List[str]:
        """팔로우 추천 사용자 목록 (팔로우하는 사람들의 팔로위 기반)"""
        raise NotImplementedError
