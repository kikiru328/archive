# app/modules/social/application/dto/social_dto.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.modules.social.domain.entity.like import Like
from app.modules.social.domain.entity.comment import Comment
from app.modules.social.domain.entity.bookmark import Bookmark


# ========================= LIKE DTOs =========================


@dataclass
class CreateLikeCommand:
    """좋아요 생성 명령"""

    curriculum_id: str
    user_id: str


@dataclass
class LikeQuery:
    """좋아요 조회 쿼리"""

    curriculum_id: Optional[str] = None
    user_id: Optional[str] = None
    page: int = 1
    items_per_page: int = 10


@dataclass
class LikeDTO:
    """좋아요 전송 객체"""

    id: str
    curriculum_id: str
    user_id: str
    created_at: datetime

    @classmethod
    def from_domain(cls, like: Like) -> "LikeDTO":
        return cls(
            id=like.id,
            curriculum_id=like.curriculum_id,
            user_id=like.user_id,
            created_at=like.created_at,
        )


@dataclass
class LikePageDTO:
    """좋아요 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    likes: List[LikeDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        likes: List[Like],
    ) -> "LikePageDTO":
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            likes=[LikeDTO.from_domain(like) for like in likes],
        )


# ========================= COMMENT DTOs =========================


@dataclass
class CreateCommentCommand:
    """댓글 생성 명령"""

    curriculum_id: str
    user_id: str
    content: str


@dataclass
class UpdateCommentCommand:
    """댓글 수정 명령"""

    comment_id: str
    user_id: str
    content: str


@dataclass
class CommentQuery:
    """댓글 조회 쿼리"""

    curriculum_id: Optional[str] = None
    user_id: Optional[str] = None
    page: int = 1
    items_per_page: int = 10


@dataclass
class CommentDTO:
    """댓글 전송 객체"""

    id: str
    curriculum_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, comment: Comment) -> "CommentDTO":
        return cls(
            id=comment.id,
            curriculum_id=comment.curriculum_id,
            user_id=comment.user_id,
            content=comment.content.value,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )


@dataclass
class CommentPageDTO:
    """댓글 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    comments: List[CommentDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        comments: List[Comment],
    ) -> "CommentPageDTO":
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            comments=[CommentDTO.from_domain(comment) for comment in comments],
        )


# ========================= BOOKMARK DTOs =========================


@dataclass
class CreateBookmarkCommand:
    """북마크 생성 명령"""

    curriculum_id: str
    user_id: str


@dataclass
class BookmarkQuery:
    """북마크 조회 쿼리"""

    user_id: Optional[str] = None
    page: int = 1
    items_per_page: int = 10


@dataclass
class BookmarkDTO:
    """북마크 전송 객체"""

    id: str
    curriculum_id: str
    user_id: str
    created_at: datetime

    @classmethod
    def from_domain(cls, bookmark: Bookmark) -> "BookmarkDTO":
        return cls(
            id=bookmark.id,
            curriculum_id=bookmark.curriculum_id,
            user_id=bookmark.user_id,
            created_at=bookmark.created_at,
        )


@dataclass
class BookmarkPageDTO:
    """북마크 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    bookmarks: List[BookmarkDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        bookmarks: List[Bookmark],
    ) -> "BookmarkPageDTO":
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            bookmarks=[BookmarkDTO.from_domain(bookmark) for bookmark in bookmarks],
        )


# ========================= 통합 DTOs =========================


@dataclass
class CurriculumSocialStatsDTO:
    """커리큘럼 소셜 통계 전송 객체"""

    curriculum_id: str
    like_count: int
    comment_count: int
    is_liked_by_user: bool
    is_bookmarked_by_user: bool


@dataclass
class UserSocialStatsDTO:
    """사용자 소셜 통계 전송 객체"""

    user_id: str
    total_likes_given: int
    total_comments_written: int
    total_bookmarks: int
    total_likes_received: int  # 자신의 커리큘럼이 받은 좋아요
    total_comments_received: int  # 자신의 커리큘럼에 달린 댓글
