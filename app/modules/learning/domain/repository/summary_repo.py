from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple

from app.modules.learning.domain.entity.summary import Summary


class ISummaryRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, summary: Summary) -> None:
        """요약 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, summary_id: str) -> Optional[Summary]:
        """ID로 요약 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum_and_week(
        self,
        curriculum_id: str,
        week_number: int,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Summary]]:
        """커리큘럼과 주차로 요약 목록 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum(
        self,
        curriculum_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Summary]]:
        """커리큘럼의 모든 요약 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user(
        self,
        owner_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Summary]]:
        """사용자의 모든 요약 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, summary: Summary) -> None:
        """요약 업데이트"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, summary_id: str) -> None:
        """요약 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 요약 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_user(self, owner_id: str) -> int:
        """사용자의 요약 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id(self, summary_id: str) -> bool:
        """요약 존재 여부 확인"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_user_since(self, owner_id: str, since_date: datetime) -> int:
        """특정 날짜 이후 사용자의 요약 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_since(
        self,
        owner_id: str,
        since_date: datetime,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Summary]]:
        """특정 날짜 이후 사용자의 요약 목록 조회"""
        raise NotImplementedError
