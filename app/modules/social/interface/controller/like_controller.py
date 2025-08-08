from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.social.application.service.like_service import LikeService
from app.modules.social.application.dto.social_dto import (
    CreateLikeCommand,
    LikeQuery,
    LikeDTO,
    LikePageDTO,
)
from app.modules.social.interface.schema.social_schema import (
    CreateLikeRequest,
    LikeResponse,
    LikePageResponse,
    LikeStatusResponse,
)
from app.modules.user.domain.vo.role import RoleVO


like_router = APIRouter(prefix="/curriculums", tags=["Likes"])


@like_router.post(
    "/{curriculum_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_like(
    curriculum_id: str,
    request: CreateLikeRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    like_service: LikeService = Depends(Provide[Container.like_service]),
) -> LikeResponse:
    """커리큘럼에 좋아요 생성"""
    command: CreateLikeCommand = request.to_command(
        curriculum_id=curriculum_id,
        user_id=current_user.id,
    )

    dto: LikeDTO = await like_service.create_like(
        command=command,
        role=RoleVO(current_user.role.value),
    )

    return LikeResponse.from_dto(dto)


@like_router.delete(
    "/{curriculum_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_like(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    like_service: LikeService = Depends(Provide[Container.like_service]),
) -> None:
    """커리큘럼의 좋아요 삭제"""
    await like_service.delete_like(
        curriculum_id=curriculum_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )


@like_router.get(
    "/{curriculum_id}/likes",
    response_model=LikePageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_likes_by_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    like_service: LikeService = Depends(Provide[Container.like_service]),
) -> LikePageResponse:
    """특정 커리큘럼의 좋아요 목록 조회"""
    query = LikeQuery(
        curriculum_id=curriculum_id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: LikePageDTO = await like_service.get_likes(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return LikePageResponse.from_dto(page_dto)


@like_router.get(
    "/{curriculum_id}/like/status",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_like_status(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    like_service: LikeService = Depends(Provide[Container.like_service]),
) -> LikeStatusResponse:
    """커리큘럼의 좋아요 상태 조회"""
    is_liked = await like_service.check_like_status(
        curriculum_id=curriculum_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    # 좋아요 수도 함께 조회
    query = LikeQuery(curriculum_id=curriculum_id, page=1, items_per_page=1)
    page_dto = await like_service.get_likes(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return LikeStatusResponse(
        is_liked=is_liked,
        like_count=page_dto.total_count,
    )


# 사용자 좋아요 관련 엔드포인트
user_like_router = APIRouter(prefix="/users/me/likes", tags=["User Likes"])


@user_like_router.get(
    "",
    response_model=LikePageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_my_likes(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    like_service: LikeService = Depends(Provide[Container.like_service]),
) -> LikePageResponse:
    """내가 한 모든 좋아요 목록 조회"""
    query = LikeQuery(
        user_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: LikePageDTO = await like_service.get_likes(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return LikePageResponse.from_dto(page_dto)
