from datetime import datetime
from typing import List, Optional
from ulid import ULID  # type: ignore

from app.core.auth import Role
from app.modules.taxonomy.application.dto.tag_dto import (
    CreateTagCommand,
    UpdateTagCommand,
    TagQuery,
    TagDTO,
    TagPageDTO,
    TagStatisticsDTO,
)
from app.modules.taxonomy.application.exception import (
    TagNotFoundError,
    DuplicateTagError,
    TagAccessDeniedError,
    InvalidTagNameError,
    TagInUseError,
)
from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.repository.tag_repo import ITagRepository
from app.modules.taxonomy.domain.service.tag_domain_service import TagDomainService
from app.modules.taxonomy.domain.vo.tag_name import TagName
from app.modules.user.domain.vo.role import RoleVO
from app.common.monitoring.metrics import increment_tag_creation


class TagService:
    """태그 애플리케이션 서비스"""

    def __init__(
        self,
        tag_repo: ITagRepository,
        tag_domain_service: TagDomainService,
        ulid: ULID = ULID(),
    ) -> None:
        self.tag_repo: ITagRepository = tag_repo
        self.tag_domain_service: TagDomainService = tag_domain_service
        self.ulid: ULID = ulid

    async def create_tag(
        self,
        command: CreateTagCommand,
        created_at: Optional[datetime] = None,
    ) -> TagDTO:
        """태그 생성"""
        try:
            # 도메인 서비스를 통한 태그 생성
            tag: Tag = await self.tag_domain_service.create_tag(
                tag_id=self.ulid.generate(),
                name=command.name,
                created_by=command.created_by,
                created_at=created_at,
            )

            await self.tag_repo.save(tag)
            increment_tag_creation()
            return TagDTO.from_domain(tag)

        except ValueError as e:
            raise InvalidTagNameError(str(e))

    async def get_tag_by_id(
        self,
        tag_id: str,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> TagDTO:
        """ID로 태그 조회"""
        tag: Tag | None = await self.tag_repo.find_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(f"Tag {tag_id} not found")

        return TagDTO.from_domain(tag)

    async def get_tag_by_name(
        self,
        name: str,
        user_id: str,
        role: RoleVO = RoleVO.USER,
    ) -> Optional[TagDTO]:
        """이름으로 태그 조회"""
        try:
            tag_name: TagName = await self.tag_domain_service.validate_tag_creation(
                name
            )
            tag: Tag | None = await self.tag_repo.find_by_name(tag_name)
            if not tag:
                return None

            return TagDTO.from_domain(tag)

        except ValueError as e:
            raise InvalidTagNameError(str(e))

    async def get_popular_tags(
        self,
        limit: int = 20,
        min_usage: int = 1,
    ) -> List[TagDTO]:
        """인기 태그 목록 조회"""
        tags: List[Tag] = await self.tag_repo.find_popular_tags(
            limit=limit,
            min_usage=min_usage,
        )
        return [TagDTO.from_domain(tag) for tag in tags]

    async def search_tags(
        self,
        query: str,
        limit: int = 10,
    ) -> List[TagDTO]:
        """태그 검색 (자동완성용)"""
        if not query.strip():
            return []

        tags: List[Tag] = await self.tag_repo.search_by_name(query.strip(), limit)
        return [TagDTO.from_domain(tag) for tag in tags]

    async def get_tags(
        self,
        query: TagQuery,
    ) -> TagPageDTO:
        """태그 목록 조회"""
        if query.search_query:
            # 검색 모드
            tags: List[Tag] = await self.tag_repo.search_by_name(
                query.search_query, query.items_per_page
            )
            total_count: int = len(tags)
            return TagPageDTO.from_domain(
                total_count=total_count,
                page=query.page,
                items_per_page=query.items_per_page,
                tags=tags,
            )
        else:
            # 전체 조회 모드
            total_count, tags = await self.tag_repo.find_all(
                page=query.page,
                items_per_page=query.items_per_page,
            )
            return TagPageDTO.from_domain(
                total_count=total_count,
                page=query.page,
                items_per_page=query.items_per_page,
                tags=tags,
            )

    async def update_tag(
        self,
        command: UpdateTagCommand,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> TagDTO:
        """태그 수정"""
        tag: Tag | None = await self.tag_repo.find_by_id(command.tag_id)
        if not tag:
            raise TagNotFoundError(f"Tag {command.tag_id} not found")

        # 권한 확인 (관리자 또는 태그 생성자만 수정 가능)
        if role != RoleVO.ADMIN and tag.created_by != user_id:
            raise TagAccessDeniedError("You can only modify your own tags")

        # 이름 변경
        if command.name and command.name.strip():
            try:
                new_name: TagName = await self.tag_domain_service.validate_tag_creation(
                    command.name
                )

                # 중복 확인 (자기 자신 제외)
                if not await self.tag_domain_service.is_tag_name_unique(
                    new_name, tag.id
                ):
                    raise DuplicateTagError(f"Tag '{command.name}' already exists")

                tag.change_name(new_name)

            except ValueError as e:
                raise InvalidTagNameError(str(e))

        await self.tag_repo.update(tag)
        return TagDTO.from_domain(tag)

    async def delete_tag(
        self,
        tag_id: str,
        user_id: str,
        role: Role | RoleVO = RoleVO.USER,
    ) -> None:
        """태그 삭제"""
        tag: Tag | None = await self.tag_repo.find_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(f"Tag {tag_id} not found")

        # 권한 확인 (관리자만 삭제 가능)
        if role != RoleVO.ADMIN:
            raise TagAccessDeniedError("Only administrators can delete tags")

        # 삭제 가능 여부 확인
        if not await self.tag_domain_service.can_delete_tag(tag_id):
            raise TagInUseError("Cannot delete tag that is currently in use")

        await self.tag_repo.delete(tag_id)

    async def increment_tag_usage(self, tag_id: str) -> None:
        """태그 사용 횟수 증가"""
        await self.tag_repo.increment_usage_count(tag_id)

    async def decrement_tag_usage(self, tag_id: str) -> None:
        """태그 사용 횟수 감소"""
        await self.tag_repo.decrement_usage_count(tag_id)

    async def find_or_create_tags_by_names(
        self,
        tag_names: List[str],
        created_by: str,
    ) -> List[TagDTO]:
        """태그 이름 리스트로 태그들을 찾거나 생성"""
        try:
            tags: List[Tag] = (
                await self.tag_domain_service.find_or_create_tags_by_names(
                    tag_names, created_by
                )
            )
            return [TagDTO.from_domain(tag) for tag in tags]

        except ValueError as e:
            raise InvalidTagNameError(str(e))

    async def get_tag_statistics(self) -> TagStatisticsDTO:
        """태그 통계 정보 조회"""
        stats = await self.tag_domain_service.get_tag_statistics()
        return TagStatisticsDTO(
            total_tags=stats["total_tags"],
            popular_tags_count=stats["popular_tags_count"],
            unused_tags_count=stats["unused_tags_count"],
            most_popular_tags=stats["most_popular_tags"],
        )
