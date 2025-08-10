from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.social.application.service.bookmark_service import BookmarkService
from app.modules.social.application.dto.social_dto import (
    CreateBookmarkCommand,
    BookmarkQuery,
    BookmarkDTO,
    BookmarkPageDTO,
)
from app.modules.social.interface.schema.social_schema import (
    CreateBookmarkRequest,
    BookmarkResponse,
    BookmarkPageResponse,
    BookmarkStatusResponse,
)
from app.modules.user.domain.vo.role import RoleVO


bookmark_router = APIRouter(prefix="/curriculums", tags=["Bookmarks"])


@bookmark_router.post(
    "/{curriculum_id}/bookmark",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_bookmark(
    curriculum_id: str,
    request: CreateBookmarkRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    bookmark_service: BookmarkService = Depends(Provide[Container.bookmark_service]),
) -> BookmarkResponse:
    """커리큘럼에 북마크 생성"""
    command: CreateBookmarkCommand = request.to_command(
        curriculum_id=curriculum_id,
        user_id=current_user.id,
    )

    dto: BookmarkDTO = await bookmark_service.create_bookmark(
        command=command,
        role=RoleVO(current_user.role.value),
    )

    return BookmarkResponse.from_dto(dto)


@bookmark_router.delete(
    "/{curriculum_id}/bookmark",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_bookmark(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    bookmark_service: BookmarkService = Depends(Provide[Container.bookmark_service]),
) -> None:
    """커리큘럼의 북마크 삭제"""
    await bookmark_service.delete_bookmark(
        curriculum_id=curriculum_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )


@bookmark_router.get(
    "/{curriculum_id}/bookmark/status",
    response_model=BookmarkStatusResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_bookmark_status(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    bookmark_service: BookmarkService = Depends(Provide[Container.bookmark_service]),
) -> BookmarkStatusResponse:
    """커리큘럼의 북마크 상태 조회"""
    is_bookmarked = await bookmark_service.check_bookmark_status(
        curriculum_id=curriculum_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return BookmarkStatusResponse(is_bookmarked=is_bookmarked)


# 사용자 북마크 관련 엔드포인트
user_bookmark_router = APIRouter(prefix="/users/me/bookmarks", tags=["User Bookmarks"])


@user_bookmark_router.get(
    "",
    response_model=BookmarkPageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_my_bookmarks(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    bookmark_service: BookmarkService = Depends(Provide[Container.bookmark_service]),
) -> BookmarkPageResponse:
    """내가 한 모든 북마크 목록 조회"""
    query = BookmarkQuery(
        user_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: BookmarkPageDTO = await bookmark_service.get_bookmarks(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return BookmarkPageResponse.from_dto(page_dto)
