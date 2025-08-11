from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from app.modules.social.application.dto.social_dto import (
    CreateLikeCommand,
    CreateCommentCommand,
    UpdateCommentCommand,
    CreateBookmarkCommand,
    LikeDTO,
    CommentDTO,
    BookmarkDTO,
    LikePageDTO,
    CommentPageDTO,
    BookmarkPageDTO,
)


# ========================= LIKE SCHEMAS =========================


class CreateLikeRequest(BaseModel):
    """좋아요 생성 요청"""

    # 요청 본문 없음 - curriculum_id는 경로에서, user_id는 인증에서 가져옴
    pass

    def to_command(self, curriculum_id: str, user_id: str) -> CreateLikeCommand:
        return CreateLikeCommand(
            curriculum_id=curriculum_id,
            user_id=user_id,
        )


class LikeResponse(BaseModel):
    """좋아요 응답"""

    id: str
    curriculum_id: str
    user_id: str
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: LikeDTO) -> "LikeResponse":
        return cls(
            id=dto.id,
            curriculum_id=dto.curriculum_id,
            user_id=dto.user_id,
            created_at=dto.created_at,
        )


class LikePageResponse(BaseModel):
    """좋아요 목록 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    likes: List[LikeResponse]

    @classmethod
    def from_dto(cls, dto: LikePageDTO) -> "LikePageResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            likes=[LikeResponse.from_dto(like) for like in dto.likes],
        )


# ========================= COMMENT SCHEMAS =========================


class CreateCommentRequest(BaseModel):
    """댓글 생성 요청"""

    content: str = Field(min_length=1, max_length=1000, description="댓글 내용")

    def to_command(self, curriculum_id: str, user_id: str) -> CreateCommentCommand:
        return CreateCommentCommand(
            curriculum_id=curriculum_id,
            user_id=user_id,
            content=self.content,
        )


class UpdateCommentRequest(BaseModel):
    """댓글 수정 요청"""

    content: str = Field(min_length=1, max_length=1000, description="수정할 댓글 내용")

    def to_command(self, comment_id: str, user_id: str) -> UpdateCommentCommand:
        return UpdateCommentCommand(
            comment_id=comment_id,
            user_id=user_id,
            content=self.content,
        )


class CommentResponse(BaseModel):
    """댓글 응답"""

    id: str
    curriculum_id: str
    user_id: str
    content: str
    content_length: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: CommentDTO) -> "CommentResponse":
        return cls(
            id=dto.id,
            curriculum_id=dto.curriculum_id,
            user_id=dto.user_id,
            content=dto.content,
            content_length=len(dto.content),
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class CommentBriefResponse(BaseModel):
    """댓글 간략 응답 (목록용)"""

    id: str
    curriculum_id: str
    user_id: str
    user_name: str  # 사용자 이름 추가
    content_snippet: str
    content_length: int
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: CommentDTO, user_name: str) -> "CommentBriefResponse":
        snippet = dto.content[:100] + "..." if len(dto.content) > 100 else dto.content
        return cls(
            id=dto.id,
            curriculum_id=dto.curriculum_id,
            user_id=dto.user_id,
            user_name=user_name or "알 수 없는 사용자",  # 사용자 이름 추가
            content_snippet=snippet,
            content_length=len(dto.content),
            created_at=dto.created_at,
        )


class CommentPageResponse(BaseModel):
    """댓글 목록 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    comments: List[CommentBriefResponse]

    @classmethod
    def from_dto(cls, dto: CommentPageDTO, user_names: dict) -> "CommentPageResponse":
        user_names = user_names or {}
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            comments=[
                CommentBriefResponse.from_dto(
                    comment, user_names.get(comment.user_id, "알 수 없는 사용자")
                )
                for comment in dto.comments
            ],
        )


# ========================= BOOKMARK SCHEMAS =========================


class CreateBookmarkRequest(BaseModel):
    """북마크 생성 요청"""

    # 요청 본문 없음 - curriculum_id는 경로에서, user_id는 인증에서 가져옴
    pass

    def to_command(self, curriculum_id: str, user_id: str) -> CreateBookmarkCommand:
        return CreateBookmarkCommand(
            curriculum_id=curriculum_id,
            user_id=user_id,
        )


class BookmarkResponse(BaseModel):
    """북마크 응답"""

    id: str
    curriculum_id: str
    user_id: str
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: BookmarkDTO) -> "BookmarkResponse":
        return cls(
            id=dto.id,
            curriculum_id=dto.curriculum_id,
            user_id=dto.user_id,
            created_at=dto.created_at,
        )


class BookmarkPageResponse(BaseModel):
    """북마크 목록 페이지 응답"""

    total_count: int
    page: int
    items_per_page: int
    bookmarks: List[BookmarkResponse]

    @classmethod
    def from_dto(cls, dto: BookmarkPageDTO) -> "BookmarkPageResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            bookmarks=[
                BookmarkResponse.from_dto(bookmark) for bookmark in dto.bookmarks
            ],
        )


# ========================= STATUS SCHEMAS =========================


class LikeStatusResponse(BaseModel):
    """좋아요 상태 응답"""

    is_liked: bool
    like_count: int


class BookmarkStatusResponse(BaseModel):
    """북마크 상태 응답"""

    is_bookmarked: bool


class CurriculumSocialStatsResponse(BaseModel):
    """커리큘럼 소셜 통계 응답"""

    curriculum_id: str
    like_count: int
    comment_count: int
    is_liked_by_user: bool
    is_bookmarked_by_user: bool


class UserSocialStatsResponse(BaseModel):
    """사용자 소셜 통계 응답"""

    user_id: str
    total_likes_given: int
    total_comments_written: int
    total_bookmarks: int
    total_likes_received: int
    total_comments_received: int
