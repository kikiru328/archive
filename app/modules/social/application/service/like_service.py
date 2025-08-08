from ulid import ULID  # type: ignore

from app.modules.social.application.dto.social_dto import (
    CreateLikeCommand,
    LikeQuery,
    LikeDTO,
    LikePageDTO,
)
from app.modules.social.application.exception import (
    LikeNotFoundError,
    LikeAlreadyExistsError,
    SocialAccessDeniedError,
    CurriculumNotAccessibleError,
)
from app.modules.social.domain.entity.like import Like
from app.modules.social.domain.repository.like_repo import ILikeRepository
from app.modules.social.domain.service.social_domain_service import SocialDomainService
from app.modules.user.domain.vo.role import RoleVO


class LikeService:
    def __init__(
        self,
        like_repo: ILikeRepository,
        social_domain_service: SocialDomainService,
        ulid: ULID = ULID(),
    ) -> None:
        self.like_repo: ILikeRepository = like_repo
        self.social_domain_service: SocialDomainService = social_domain_service
        self.ulid: ULID = ulid

    async def create_like(
        self,
        command: CreateLikeCommand,
        role: RoleVO,
    ) -> LikeDTO:
        """좋아요 생성"""
        # 좋아요 생성 유효성 검증
        is_valid: bool = await self.social_domain_service.validate_like_creation(
            command.curriculum_id, command.user_id, role
        )

        if not is_valid:
            # 이미 존재하는지 확인
            existing_like: bool = await self.like_repo.exists_by_curriculum_and_user(
                command.curriculum_id, command.user_id
            )
            if existing_like:
                raise LikeAlreadyExistsError("Like already exists for this curriculum")
            else:
                raise CurriculumNotAccessibleError("Cannot like this curriculum")

        like: Like = await self.social_domain_service.create_like(
            like_id=self.ulid.generate(),
            curriculum_id=command.curriculum_id,
            user_id=command.user_id,
        )

        await self.like_repo.save(like)
        return LikeDTO.from_domain(like)

    async def delete_like(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> None:
        """좋아요 삭제"""
        # 커리큘럼 접근 권한 확인
        can_access: bool = await self.social_domain_service.can_access_curriculum(
            curriculum_id, user_id, role
        )
        if not can_access:
            raise CurriculumNotAccessibleError("Cannot access this curriculum")

        # 좋아요 존재 확인
        like: Like | None = await self.like_repo.find_by_curriculum_and_user(
            curriculum_id, user_id
        )
        if not like:
            raise LikeNotFoundError("Like not found")

        # 권한 확인 (자신의 좋아요이거나 관리자)
        if role != RoleVO.ADMIN and not like.is_liked_by(user_id):
            raise SocialAccessDeniedError("You can only delete your own likes")

        await self.like_repo.delete_by_curriculum_and_user(curriculum_id, user_id)

    async def get_likes(
        self,
        query: LikeQuery,
        user_id: str,
        role: RoleVO,
    ) -> LikePageDTO:
        """좋아요 목록 조회"""
        if query.curriculum_id:
            # 특정 커리큘럼의 좋아요들
            can_access: bool = await self.social_domain_service.can_access_curriculum(
                query.curriculum_id, user_id, role
            )
            if not can_access:
                raise CurriculumNotAccessibleError("Cannot access this curriculum")

            total_count, likes = await self.like_repo.find_by_curriculum(
                curriculum_id=query.curriculum_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        elif query.user_id:
            # 특정 사용자의 좋아요들 (본인이거나 관리자만)
            if role != RoleVO.ADMIN and query.user_id != user_id:
                raise SocialAccessDeniedError("You can only view your own likes")

            total_count, likes = await self.like_repo.find_by_user(
                user_id=query.user_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        else:
            # 자신의 좋아요들
            total_count, likes = await self.like_repo.find_by_user(
                user_id=user_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )

        return LikePageDTO.from_domain(
            total_count=total_count,
            page=query.page,
            items_per_page=query.items_per_page,
            likes=likes,
        )

    async def check_like_status(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """사용자가 커리큘럼에 좋아요를 했는지 확인"""
        can_access = await self.social_domain_service.can_access_curriculum(
            curriculum_id, user_id, role
        )
        if not can_access:
            return False

        return await self.like_repo.exists_by_curriculum_and_user(
            curriculum_id, user_id
        )
