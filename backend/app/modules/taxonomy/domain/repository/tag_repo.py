from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.vo.tag_name import TagName


class ITagRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, tag: Tag) -> None:
        """태그 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, tag_id: str) -> Optional[Tag]:
        """ID로 태그 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_name(self, name: TagName) -> Optional[Tag]:
        """이름으로 태그 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_or_create_by_names(
        self, tag_names: List[TagName], created_by: str
    ) -> List[Tag]:
        """태그 이름 리스트로 태그들을 찾거나 생성"""
        raise NotImplementedError

    @abstractmethod
    async def find_popular_tags(self, limit: int = 20, min_usage: int = 1) -> List[Tag]:
        """인기 태그 조회 (사용횟수 기준)"""
        raise NotImplementedError

    @abstractmethod
    async def search_by_name(self, query: str, limit: int = 10) -> List[Tag]:
        """태그 이름으로 검색 (자동완성용)"""
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self, page: int = 1, items_per_page: int = 20
    ) -> Tuple[int, List[Tag]]:
        """모든 태그 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_creator(
        self, creator_id: str, page: int = 1, items_per_page: int = 20
    ) -> Tuple[int, List[Tag]]:
        """생성자별 태그 조회 (페이징)"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, tag: Tag) -> None:
        """태그 업데이트"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, tag_id: str) -> None:
        """태그 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def increment_usage_count(self, tag_id: str) -> None:
        """태그 사용 횟수 증가"""
        raise NotImplementedError

    @abstractmethod
    async def decrement_usage_count(self, tag_id: str) -> None:
        """태그 사용 횟수 감소"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_name(self, name: TagName) -> bool:
        """태그 이름으로 존재 여부 확인"""
        raise NotImplementedError

    @abstractmethod
    async def count_all(self) -> int:
        """전체 태그 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_usage_range(self, min_usage: int, max_usage: int) -> int:
        """사용 횟수 범위별 태그 수 조회"""
        raise NotImplementedError
