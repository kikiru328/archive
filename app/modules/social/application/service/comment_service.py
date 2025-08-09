from ulid import ULID  # type: ignore

from app.modules.social.application.dto.social_dto import (
    CreateCommentCommand,
    UpdateCommentCommand,
    CommentQuery,
    CommentDTO,
    CommentPageDTO,
)
from app.modules.social.application.exception import (
    CommentNotFoundError,
    CommentAccessDeniedError,
    InvalidCommentContentError,
    CurriculumNotAccessibleError,
)
from app.modules.social.domain.entity.comment import Comment
from app.modules.social.domain.repository.comment_repo import ICommentRepository
from app.modules.social.domain.service.social_domain_service import SocialDomainService
from app.modules.social.domain.vo.comment_content import CommentContent
from app.modules.user.domain.vo.role import RoleVO
from app.common.monitoring.metrics import increment_comment_creation


class CommentService:
    def __init__(
        self,
        comment_repo: ICommentRepository,
        social_domain_service: SocialDomainService,
        ulid: ULID = ULID(),
    ) -> None:
        self.comment_repo: ICommentRepository = comment_repo
        self.social_domain_service: SocialDomainService = social_domain_service
        self.ulid = ulid

    async def create_comment(
        self,
        command: CreateCommentCommand,
        role: RoleVO,
    ) -> CommentDTO:
        """댓글 생성"""
        # 댓글 권한 확인
        can_comment: bool = await self.social_domain_service.can_comment_on_curriculum(
            command.curriculum_id, command.user_id, role
        )
        if not can_comment:
            raise CurriculumNotAccessibleError("Cannot comment on this curriculum")

        try:
            comment: Comment = await self.social_domain_service.create_comment(
                comment_id=self.ulid.generate(),
                curriculum_id=command.curriculum_id,
                user_id=command.user_id,
                content=command.content,
            )
        except ValueError as e:
            raise InvalidCommentContentError(str(e))

        await self.comment_repo.save(comment)
        increment_comment_creation()
        return CommentDTO.from_domain(comment)

    async def update_comment(
        self,
        command: UpdateCommentCommand,
        role: RoleVO,
    ) -> CommentDTO:
        """댓글 수정"""
        comment: Comment | None = await self.comment_repo.find_by_id(command.comment_id)
        if not comment:
            raise CommentNotFoundError(f"Comment {command.comment_id} not found")

        # 수정 권한 확인
        can_modify: bool = await self.social_domain_service.can_modify_comment(
            comment, command.user_id, role
        )
        if not can_modify:
            raise CommentAccessDeniedError("You can only modify your own comments")

        try:
            comment.update_content(CommentContent(command.content))
        except ValueError as e:
            raise InvalidCommentContentError(str(e))

        await self.comment_repo.update(comment)
        return CommentDTO.from_domain(comment)

    async def delete_comment(
        self,
        comment_id: str,
        user_id: str,
        role: RoleVO,
    ) -> None:
        """댓글 삭제"""
        comment: Comment | None = await self.comment_repo.find_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(f"Comment {comment_id} not found")

        # 삭제 권한 확인
        can_modify: bool = await self.social_domain_service.can_modify_comment(
            comment, user_id, role
        )
        if not can_modify:
            raise CommentAccessDeniedError("You can only delete your own comments")

        await self.comment_repo.delete(comment_id)

    async def get_comment_by_id(
        self,
        comment_id: str,
        user_id: str,
        role: RoleVO,
    ) -> CommentDTO:
        """ID로 댓글 조회"""
        comment: Comment | None = await self.comment_repo.find_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(f"Comment {comment_id} not found")

        # 커리큘럼 접근 권한 확인
        can_access: bool = await self.social_domain_service.can_access_curriculum(
            comment.curriculum_id, user_id, role
        )
        if not can_access:
            raise CurriculumNotAccessibleError("Cannot access this curriculum")

        return CommentDTO.from_domain(comment)

    async def get_comments(
        self,
        query: CommentQuery,
        user_id: str,
        role: RoleVO,
    ) -> CommentPageDTO:
        """댓글 목록 조회"""
        if query.curriculum_id:
            # 특정 커리큘럼의 댓글들
            can_access: bool = await self.social_domain_service.can_access_curriculum(
                query.curriculum_id, user_id, role
            )
            if not can_access:
                raise CurriculumNotAccessibleError("Cannot access this curriculum")

            total_count, comments = await self.comment_repo.find_by_curriculum(
                curriculum_id=query.curriculum_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        elif query.user_id:
            # 특정 사용자의 댓글들 (본인이거나 관리자만)
            if role != RoleVO.ADMIN and query.user_id != user_id:
                raise CommentAccessDeniedError("You can only view your own comments")

            total_count, comments = await self.comment_repo.find_by_user(
                user_id=query.user_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        else:
            # 자신의 댓글들
            total_count, comments = await self.comment_repo.find_by_user(
                user_id=user_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )

        return CommentPageDTO.from_domain(
            total_count=total_count,
            page=query.page,
            items_per_page=query.items_per_page,
            comments=comments,
        )
