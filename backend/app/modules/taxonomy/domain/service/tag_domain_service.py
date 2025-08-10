from datetime import datetime, timezone
from typing import List, Optional

from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.entity.category import Category
from app.modules.taxonomy.domain.entity.curriculum_tag import CurriculumTag
from app.modules.taxonomy.domain.repository.tag_repo import ITagRepository
from app.modules.taxonomy.domain.repository.category_repo import ICategoryRepository
from app.modules.taxonomy.domain.repository.curriculum_tag_repo import (
    ICurriculumTagRepository,
    ICurriculumCategoryRepository,
)
from app.modules.taxonomy.domain.vo.tag_name import TagName
from app.modules.taxonomy.domain.vo.category_name import CategoryName
from app.modules.taxonomy.domain.vo.tag_color import TagColor


class TagDomainService:
    """Tag 도메인 서비스"""

    def __init__(
        self,
        tag_repo: ITagRepository,
        category_repo: ICategoryRepository,
        curriculum_tag_repo: ICurriculumTagRepository,
        curriculum_category_repo: ICurriculumCategoryRepository,
    ) -> None:
        self.tag_repo = tag_repo
        self.category_repo = category_repo
        self.curriculum_tag_repo = curriculum_tag_repo
        self.curriculum_category_repo = curriculum_category_repo

    # ========================= TAG 관련 도메인 서비스 =========================

    async def create_tag(
        self,
        tag_id: str,
        name: str,
        created_by: str,
        created_at: Optional[datetime] = None,
    ) -> Tag:
        """태그 생성"""
        now = created_at or datetime.now(timezone.utc)
        tag_name = TagName(name)

        # 중복 확인 후 기존 태그 반환 또는 새 태그 생성
        existing_tag = await self.tag_repo.find_by_name(tag_name)
        if existing_tag:
            return existing_tag

        tag = Tag(
            id=tag_id,
            name=tag_name,
            usage_count=0,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )

        return tag

    async def is_tag_name_unique(
        self, name: TagName, exclude_tag_id: Optional[str] = None
    ) -> bool:
        """태그 이름 유일성 확인"""
        existing_tag = await self.tag_repo.find_by_name(name)
        if not existing_tag:
            return True

        # 자기 자신 제외
        if exclude_tag_id and existing_tag.id == exclude_tag_id:
            return True

        return False

    async def validate_tag_creation(self, name: str) -> TagName:
        """태그 생성 유효성 검증"""
        return TagName(name)

    async def find_or_create_tags_by_names(
        self, tag_names: List[str], created_by: str
    ) -> List[Tag]:
        """태그 이름 리스트로 태그들을 찾거나 생성"""
        tag_name_vos = TagName.from_list(tag_names)
        return await self.tag_repo.find_or_create_by_names(tag_name_vos, created_by)

    async def can_delete_tag(self, tag_id: str) -> bool:
        """태그 삭제 가능 여부 확인"""
        tag = await self.tag_repo.find_by_id(tag_id)
        if not tag:
            return False

        # 사용되지 않는 태그만 삭제 가능
        return tag.can_be_deleted()

    # ========================= CATEGORY 관련 도메인 서비스 =========================

    async def create_category(
        self,
        category_id: str,
        name: str,
        description: Optional[str],
        color: str,
        icon: Optional[str] = None,
        sort_order: int = 0,
        created_at: Optional[datetime] = None,
    ) -> Category:
        """카테고리 생성"""
        now = created_at or datetime.now(timezone.utc)
        category_name = CategoryName(name)
        category_color = TagColor(color)

        category = Category(
            id=category_id,
            name=category_name,
            description=description,
            color=category_color,
            icon=icon,
            sort_order=sort_order,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return category

    async def is_category_name_unique(
        self, name: CategoryName, exclude_category_id: Optional[str] = None
    ) -> bool:
        """카테고리 이름 유일성 확인"""
        existing_category = await self.category_repo.find_by_name(name)
        if not existing_category:
            return True

        # 자기 자신 제외
        if exclude_category_id and existing_category.id == exclude_category_id:
            return True

        return False

    async def validate_category_creation(
        self, name: str, exclude_category_id: Optional[str] = None
    ) -> CategoryName:
        """카테고리 생성 유효성 검증"""
        category_name = CategoryName(name)

        # 중복 확인
        if not await self.is_category_name_unique(category_name, exclude_category_id):
            raise ValueError(f"Category '{name}' already exists")

        return category_name

    async def can_delete_category(self, category_id: str) -> bool:
        """카테고리 삭제 가능 여부 확인"""
        category = await self.category_repo.find_by_id(category_id)
        if not category:
            return False

        # 사용 중인 카테고리인지 확인
        curriculum_count = await self.curriculum_category_repo.count_by_category(
            category_id
        )
        if curriculum_count > 0:
            return False

        return category.can_be_deleted()

    async def get_next_sort_order(self) -> int:
        """다음 정렬 순서 조회"""
        max_order = await self.category_repo.get_max_sort_order()
        return max_order + 1

    # ========================= CURRICULUM-TAG 관련 도메인 서비스 =========================

    async def add_tags_to_curriculum(
        self,
        curriculum_id: str,
        tag_names: List[str],
        user_id: str,
    ) -> List[Tag]:
        """커리큘럼에 태그들 추가"""
        # 태그들을 찾거나 생성
        tags = await self.find_or_create_tags_by_names(tag_names, user_id)

        now = datetime.now(timezone.utc)
        added_tags = []

        for tag in tags:
            # 이미 연결되어 있는지 확인
            if not await self.curriculum_tag_repo.exists_by_curriculum_and_tag(
                curriculum_id, tag.id
            ):
                # 새 연결 생성
                curriculum_tag = CurriculumTag(
                    id=f"{curriculum_id}_{tag.id}",  # 복합 키 형태
                    curriculum_id=curriculum_id,
                    tag_id=tag.id,
                    added_by=user_id,
                    created_at=now,
                )
                await self.curriculum_tag_repo.save(curriculum_tag)

                # 태그 사용횟수 증가
                await self.tag_repo.increment_usage_count(tag.id)
                added_tags.append(tag)

        return added_tags

    async def remove_tag_from_curriculum(
        self, curriculum_id: str, tag_name: str
    ) -> None:
        """커리큘럼에서 태그 제거"""
        tag_name_vo = TagName(tag_name)
        tag = await self.tag_repo.find_by_name(tag_name_vo)

        if not tag:
            raise ValueError(f"Tag '{tag_name}' not found")

        # 연결 삭제
        await self.curriculum_tag_repo.delete_by_curriculum_and_tag(
            curriculum_id, tag.id
        )

        # 태그 사용횟수 감소
        await self.tag_repo.decrement_usage_count(tag.id)

    async def validate_curriculum_tag_limit(
        self, curriculum_id: str, max_tags: int = 10
    ) -> bool:
        """커리큘럼 태그 개수 제한 검증"""
        current_count = await self.curriculum_tag_repo.count_by_curriculum(
            curriculum_id
        )
        return current_count < max_tags

    # ========================= CURRICULUM-CATEGORY 관련 도메인 서비스 =========================

    async def assign_category_to_curriculum(
        self,
        curriculum_id: str,
        category_id: str,
        user_id: str,
    ) -> Category:
        """커리큘럼에 카테고리 할당"""
        category = await self.category_repo.find_by_id(category_id)
        if not category or not category.is_active:
            raise ValueError(f"Active category {category_id} not found")

        # 기존 카테고리가 있으면 교체, 없으면 새로 할당
        await self.curriculum_category_repo.update_curriculum_category(
            curriculum_id, category_id, user_id
        )

        return category

    async def remove_category_from_curriculum(self, curriculum_id: str) -> None:
        """커리큘럼에서 카테고리 제거"""
        await self.curriculum_category_repo.delete_by_curriculum(curriculum_id)

    async def validate_category_assignment(self, category_id: str) -> bool:
        """카테고리 할당 유효성 검증"""
        category = await self.category_repo.find_by_id(category_id)
        return category is not None and category.is_active

    # ========================= 통계 및 분석 =========================

    async def get_tag_statistics(self) -> dict:
        """태그 통계 정보 조회"""
        total_tags = await self.tag_repo.count_all()
        popular_tags = await self.tag_repo.find_popular_tags(limit=10)
        unused_tags = await self.tag_repo.count_by_usage_range(0, 0)

        return {
            "total_tags": total_tags,
            "popular_tags_count": len(popular_tags),
            "unused_tags_count": unused_tags,
            "most_popular_tags": [tag.name.value for tag in popular_tags[:5]],
        }

    async def get_category_statistics(self) -> dict:
        """카테고리 통계 정보 조회"""
        total_categories = await self.category_repo.count_all(include_inactive=True)
        active_categories = await self.category_repo.count_active()

        return {
            "total_categories": total_categories,
            "active_categories": active_categories,
            "inactive_categories": total_categories - active_categories,
        }
