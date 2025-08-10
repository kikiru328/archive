from datetime import datetime, timezone
from typing import Optional

from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.social.domain.entity.like import Like
from app.modules.social.domain.entity.comment import Comment
from app.modules.social.domain.entity.bookmark import Bookmark
from app.modules.social.domain.repository.like_repo import ILikeRepository
from app.modules.social.domain.repository.comment_repo import ICommentRepository
from app.modules.social.domain.repository.bookmark_repo import IBookmarkRepository
from app.modules.social.domain.vo.comment_content import CommentContent
from app.modules.user.domain.vo.role import RoleVO


class SocialDomainService:
    """Social 도메인 서비스"""

    def __init__(
        self,
        like_repo: ILikeRepository,
        comment_repo: ICommentRepository,
        bookmark_repo: IBookmarkRepository,
        curriculum_repo: ICurriculumRepository,
    ) -> None:
        self.like_repo: ILikeRepository = like_repo
        self.comment_repo: ICommentRepository = comment_repo
        self.bookmark_repo: IBookmarkRepository = bookmark_repo
        self.curriculum_repo: ICurriculumRepository = curriculum_repo

    # ========================= LIKE 관련 도메인 서비스 =========================

    async def create_like(
        self,
        like_id: str,
        curriculum_id: str,
        user_id: str,
        created_at: Optional[datetime] = None,
    ) -> Like:
        """좋아요 생성"""
        now: datetime = created_at or datetime.now(timezone.utc)

        like = Like(
            id=like_id,
            curriculum_id=curriculum_id,
            user_id=user_id,
            created_at=now,
        )

        return like

    async def can_like_curriculum(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """커리큘럼에 좋아요를 할 수 있는지 확인"""
        # 커리큘럼 존재 및 접근 권한 확인
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id if role != RoleVO.ADMIN else None,
        )

        if not curriculum:
            return False

        # 자신의 커리큘럼이거나 공개 커리큘럼인 경우 좋아요 가능
        return curriculum.is_owned_by(user_id) or curriculum.is_public()

    async def validate_like_creation(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """좋아요 생성 유효성 검증"""
        # 이미 좋아요가 존재하는지 확인
        existing_like: bool = await self.like_repo.exists_by_curriculum_and_user(
            curriculum_id, user_id
        )
        if existing_like:
            return False

        # 좋아요 권한 확인
        return await self.can_like_curriculum(curriculum_id, user_id, role)

    # ========================= COMMENT 관련 도메인 서비스 =========================

    async def create_comment(
        self,
        comment_id: str,
        curriculum_id: str,
        user_id: str,
        content: str,
        created_at: Optional[datetime] = None,
    ) -> Comment:
        """댓글 생성"""
        now: datetime = created_at or datetime.now(timezone.utc)

        comment = Comment(
            id=comment_id,
            curriculum_id=curriculum_id,
            user_id=user_id,
            content=CommentContent(content),
            created_at=now,
            updated_at=now,
        )

        return comment

    async def can_comment_on_curriculum(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """커리큘럼에 댓글을 달 수 있는지 확인"""
        # 커리큘럼 존재 및 접근 권한 확인
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id if role != RoleVO.ADMIN else None,
        )

        if not curriculum:
            return False

        # 자신의 커리큘럼이거나 공개 커리큘럼인 경우 댓글 가능
        return curriculum.is_owned_by(user_id) or curriculum.is_public()

    async def can_modify_comment(
        self,
        comment: Comment,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """댓글을 수정할 수 있는지 확인"""
        # 관리자이거나 댓글 작성자인 경우 수정 가능
        return role == RoleVO.ADMIN or comment.is_written_by(user_id)

    # ========================= BOOKMARK 관련 도메인 서비스 =========================

    async def create_bookmark(
        self,
        bookmark_id: str,
        curriculum_id: str,
        user_id: str,
        created_at: Optional[datetime] = None,
    ) -> Bookmark:
        """북마크 생성"""
        now: datetime = created_at or datetime.now(timezone.utc)

        bookmark = Bookmark(
            id=bookmark_id,
            curriculum_id=curriculum_id,
            user_id=user_id,
            created_at=now,
        )

        return bookmark

    async def can_bookmark_curriculum(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """커리큘럼을 북마크할 수 있는지 확인"""
        # 커리큘럼 존재 및 접근 권한 확인
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id if role != RoleVO.ADMIN else None,
        )

        if not curriculum:
            return False

        # 자신의 커리큘럼이거나 공개 커리큘럼인 경우 북마크 가능
        return curriculum.is_owned_by(user_id) or curriculum.is_public()

    async def validate_bookmark_creation(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """북마크 생성 유효성 검증"""
        # 이미 북마크가 존재하는지 확인
        existing_bookmark: bool = (
            await self.bookmark_repo.exists_by_curriculum_and_user(
                curriculum_id, user_id
            )
        )
        if existing_bookmark:
            return False

        # 북마크 권한 확인
        return await self.can_bookmark_curriculum(curriculum_id, user_id, role)

    # ========================= 공통 권한 검증 =========================

    async def can_access_curriculum(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> bool:
        """커리큘럼에 접근할 수 있는지 확인"""
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=user_id if role != RoleVO.ADMIN else None,
        )

        if not curriculum:
            return False

        # 관리자, 소유자, 또는 공개 커리큘럼인 경우 접근 가능
        return (
            role == RoleVO.ADMIN
            or curriculum.is_owned_by(user_id)
            or curriculum.is_public()
        )
