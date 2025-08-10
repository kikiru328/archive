from typing import Annotated
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.social.application.dto.social_dto import (
    CommentPageDTO,
    CommentQuery,
    LikePageDTO,
    LikeQuery,
)
from app.modules.social.application.service.like_service import LikeService
from app.modules.social.application.service.comment_service import CommentService
from app.modules.social.application.service.bookmark_service import BookmarkService
from app.modules.social.interface.schema.social_schema import (
    CurriculumSocialStatsResponse,
)
from app.modules.user.domain.vo.role import RoleVO


social_router = APIRouter(prefix="/curriculums", tags=["Social"])


@social_router.get(
    "/{curriculum_id}/social-stats",
    response_model=CurriculumSocialStatsResponse,
)
@inject
async def get_curriculum_social_stats(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    like_service: LikeService = Depends(Provide[Container.like_service]),
    comment_service: CommentService = Depends(Provide[Container.comment_service]),
    bookmark_service: BookmarkService = Depends(Provide[Container.bookmark_service]),
) -> CurriculumSocialStatsResponse:
    """커리큘럼의 종합 소셜 통계 조회"""
    role = RoleVO(current_user.role.value)

    # 좋아요 상태 및 수
    is_liked: bool = await like_service.check_like_status(
        curriculum_id, current_user.id, role
    )
    like_query = LikeQuery(curriculum_id=curriculum_id, page=1, items_per_page=1)
    like_page: LikePageDTO = await like_service.get_likes(
        like_query, current_user.id, role
    )

    # 댓글 수
    comment_query = CommentQuery(curriculum_id=curriculum_id, page=1, items_per_page=1)
    comment_page: CommentPageDTO = await comment_service.get_comments(
        comment_query, current_user.id, role
    )

    # 북마크 상태
    is_bookmarked: bool = await bookmark_service.check_bookmark_status(
        curriculum_id, current_user.id, role
    )

    return CurriculumSocialStatsResponse(
        curriculum_id=curriculum_id,
        like_count=like_page.total_count,
        comment_count=comment_page.total_count,
        is_liked_by_user=is_liked,
        is_bookmarked_by_user=is_bookmarked,
    )
