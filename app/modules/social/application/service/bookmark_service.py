from ulid import ULID  # type: ignore

from app.modules.social.application.dto.social_dto import (
    CreateBookmarkCommand,
    BookmarkQuery,
    BookmarkDTO,
    BookmarkPageDTO,
)
from app.modules.social.application.exception import (
    BookmarkNotFoundError,
    BookmarkAlreadyExistsError,
    SocialAccessDeniedError,
    CurriculumNotAccessibleError,
)
from app.modules.social.domain.entity.bookmark import Bookmark
from app.modules.social.domain.repository.bookmark_repo import IBookmarkRepository
from app.modules.social.domain.service.social_domain_service import SocialDomainService
from app.modules.user.domain.vo.role import RoleVO
from app.common.monitoring.metrics import increment_bookmark_creation


class BookmarkService:
    def __init__(
        self,
        bookmark_repo: IBookmarkRepository,
        social_domain_service: SocialDomainService,
        ulid: ULID = ULID(),
    ) -> None:
        self.bookmark_repo: IBookmarkRepository = bookmark_repo
        self.social_domain_service: SocialDomainService = social_domain_service
        self.ulid: ULID = ulid

    async def create_bookmark(
        self,
        command: CreateBookmarkCommand,
        role: RoleVO,
    ) -> BookmarkDTO:
        """북마크 생성"""
        # 북마크 생성 유효성 검증
        is_valid: bool = await self.social_domain_service.validate_bookmark_creation(
            command.curriculum_id, command.user_id, role
        )

        if not is_valid:
            # 이미 존재하는지 확인
            existing_bookmark: bool = (
                await self.bookmark_repo.exists_by_curriculum_and_user(
                    command.curriculum_id, command.user_id
                )
            )
            if existing_bookmark:
                raise BookmarkAlreadyExistsError(
                    "Bookmark already exists for this curriculum"
                )
            else:
                raise CurriculumNotAccessibleError("Cannot bookmark this curriculum")

        bookmark: Bookmark = await self.social_domain_service.create_bookmark(
            bookmark_id=self.ulid.generate(),
            curriculum_id=command.curriculum_id,
            user_id=command.user_id,
        )

        await self.bookmark_repo.save(bookmark)
        increment_bookmark_creation()
        return BookmarkDTO.from_domain(bookmark)

    async def delete_bookmark(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> None:
        """북마크 삭제"""
        # 커리큘럼 접근 권한 확인
        can_access: bool = await self.social_domain_service.can_access_curriculum(
            curriculum_id, user_id, role
        )
        if not can_access:
            raise CurriculumNotAccessibleError("Cannot access this curriculum")

        # 북마크 존재 확인
        bookmark: Bookmark | None = (
            await self.bookmark_repo.find_by_curriculum_and_user(curriculum_id, user_id)
        )
        if not bookmark:
            raise BookmarkNotFoundError("Bookmark not found")

        # 권한 확인 (자신의 북마크이거나 관리자)
        if role != RoleVO.ADMIN and not bookmark.is_bookmarked_by(user_id):
            raise SocialAccessDeniedError("You can only delete your own bookmarks")

        await self.bookmark_repo.delete_by_curriculum_and_user(curriculum_id, user_id)

    async def get_bookmarks(
        self,
        query: BookmarkQuery,
        user_id: str,
        role: RoleVO,
    ) -> BookmarkPageDTO:
        """북마크 목록 조회"""
        if query.user_id:
            # 특정 사용자의 북마크들 (본인이거나 관리자만)
            if role != RoleVO.ADMIN and query.user_id != user_id:
                raise SocialAccessDeniedError("You can only view your own bookmarks")

            total_count, bookmarks = await self.bookmark_repo.find_by_user(
                user_id=query.user_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        else:
            # 자신의 북마크들
            total_count, bookmarks = await self.bookmark_repo.find_by_user(
                user_id=user_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )

        return BookmarkPageDTO.from_domain(
            total_count=total_count,
            page=query.page,
            items_per_page=query.items_per_page,
            bookmarks=bookmarks,
        )

    async def check_bookmark_status(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """사용자가 커리큘럼을 북마크했는지 확인"""
        can_access: bool = await self.social_domain_service.can_access_curriculum(
            curriculum_id, user_id, role
        )
        if not can_access:
            return False

        return await self.bookmark_repo.exists_by_curriculum_and_user(
            curriculum_id, user_id
        )
