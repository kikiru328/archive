from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from app.modules.taxonomy.domain.entity.curriculum_tag import (
    CurriculumTag,
    CurriculumCategory,
)
from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.entity.category import Category


class ICurriculumTagRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, curriculum_tag: CurriculumTag) -> None:
        """커리큘럼-태그 연결 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, curriculum_tag_id: str) -> Optional[CurriculumTag]:
        """ID로 커리큘럼-태그 연결 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum_and_tag(
        self, curriculum_id: str, tag_id: str
    ) -> Optional[CurriculumTag]:
        """커리큘럼과 태그로 연결 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_tags_by_curriculum(self, curriculum_id: str) -> List[Tag]:
        """커리큘럼에 연결된 모든 태그 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_curriculums_by_tag(
        self, tag_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """특정 태그가 연결된 커리큘럼 ID 목록 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_curriculums_by_tag_names(
        self, tag_names: List[str], page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """여러 태그 이름으로 커리큘럼 검색 (교집합)"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[CurriculumTag]]:
        """사용자가 추가한 태그 연결 조회"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, curriculum_tag_id: str) -> None:
        """커리큘럼-태그 연결 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_curriculum_and_tag(
        self, curriculum_id: str, tag_id: str
    ) -> None:
        """커리큘럼과 태그로 연결 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_all_by_curriculum(self, curriculum_id: str) -> None:
        """커리큘럼의 모든 태그 연결 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_all_by_tag(self, tag_id: str) -> None:
        """태그의 모든 커리큘럼 연결 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 태그 수 조회"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_tag(self, tag_id: str) -> int:
        """특정 태그를 사용하는 커리큘럼 수"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_curriculum_and_tag(
        self, curriculum_id: str, tag_id: str
    ) -> bool:
        """커리큘럼-태그 연결 존재 여부 확인"""
        raise NotImplementedError


class ICurriculumCategoryRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, curriculum_category: CurriculumCategory) -> None:
        """커리큘럼-카테고리 연결 저장"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(
        self, curriculum_category_id: str
    ) -> Optional[CurriculumCategory]:
        """ID로 커리큘럼-카테고리 연결 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_curriculum(
        self, curriculum_id: str
    ) -> Optional[CurriculumCategory]:
        """커리큘럼의 카테고리 연결 조회 (1:1 관계)"""
        raise NotImplementedError

    @abstractmethod
    async def find_category_by_curriculum(
        self, curriculum_id: str
    ) -> Optional[Category]:
        """커리큘럼에 연결된 카테고리 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_curriculums_by_category(
        self, category_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """특정 카테고리의 커리큘럼 ID 목록 조회"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[CurriculumCategory]]:
        """사용자가 할당한 카테고리 연결 조회"""
        raise NotImplementedError

    @abstractmethod
    async def update_curriculum_category(
        self, curriculum_id: str, new_category_id: str, assigned_by: str
    ) -> None:
        """커리큘럼의 카테고리 변경 (기존 삭제 후 새로 생성)"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, curriculum_category_id: str) -> None:
        """커리큘럼-카테고리 연결 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_curriculum(self, curriculum_id: str) -> None:
        """커리큘럼의 카테고리 연결 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def delete_all_by_category(self, category_id: str) -> None:
        """카테고리의 모든 커리큘럼 연결 삭제"""
        raise NotImplementedError

    @abstractmethod
    async def count_by_category(self, category_id: str) -> int:
        """특정 카테고리를 사용하는 커리큘럼 수"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_curriculum(self, curriculum_id: str) -> bool:
        """커리큘럼에 카테고리가 할당되어 있는지 확인"""
        raise NotImplementedError
