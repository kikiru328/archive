from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple

from app.modules.learning.domain.entity.feedback import Feedback


class IFeedbackRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, feedback: Feedback) -> None:
        """피드백 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, feedback_id: str) -> Optional[Feedback]:
        """ID로 피드백 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_summary_id(self, summary_id: str) -> Optional[Feedback]:
        """요약 ID로 피드백 조회 (1:1 관계)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum(
        self,
        curriculum_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Feedback]]:
        """커리큘럼의 모든 피드백 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user(
        self,
        owner_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Feedback]]:
        """사용자의 모든 피드백 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_score_range(
        self,
        min_score: float,
        max_score: float,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Feedback]]:
        """점수 범위로 피드백 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, feedback: Feedback) -> None:
        """피드백 업데이트"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, feedback_id: str) -> None:
        """피드백 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 피드백 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_user(self, owner_id: str) -> int:
        """사용자의 피드백 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def get_average_score_by_curriculum(
        self, curriculum_id: str
    ) -> Optional[float]:
        """커리큘럼의 평균 점수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def get_average_score_by_user(self, owner_id: str) -> Optional[float]:
        """사용자의 평균 점수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_summary_id(self, summary_id: str) -> bool:
        """요약에 대한 피드백 존재 여부 확인"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_user_since(self, owner_id: str, since_date: datetime) -> int:
        """특정 날짜 이후 사용자의 피드백 개수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_since(
        self,
        owner_id: str,
        since_date: datetime,
        page: int = 1,
        items_per_page: int = 10,
    ) -> Tuple[int, List[Feedback]]:
        """특정 날짜 이후 사용자의 피드백 목록 조회"""
        raise NotImplementedError

    @abstractmethod
    async def get_grade_distribution_by_user(self, owner_id: str) -> dict:
        """사용자의 등급별 피드백 분포 조회"""
        raise NotImplementedError
