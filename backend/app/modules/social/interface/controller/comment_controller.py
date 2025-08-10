from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.social.application.service.comment_service import CommentService
from app.modules.social.application.dto.social_dto import (
    CreateCommentCommand,
    UpdateCommentCommand,
    CommentQuery,
    CommentDTO,
    CommentPageDTO,
)
from app.modules.social.interface.schema.social_schema import (
    CreateCommentRequest,
    UpdateCommentRequest,
    CommentResponse,
    CommentPageResponse,
)
from app.modules.user.domain.vo.role import RoleVO


comment_router = APIRouter(prefix="/curriculums", tags=["Social"])


@comment_router.post(
    "/{curriculum_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_comment(
    curriculum_id: str,
    request: CreateCommentRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    comment_service: CommentService = Depends(Provide[Container.comment_service]),
) -> CommentResponse:
    """커리큘럼에 댓글 생성"""
    command: CreateCommentCommand = request.to_command(
        curriculum_id=curriculum_id,
        user_id=current_user.id,
    )

    dto: CommentDTO = await comment_service.create_comment(
        command=command,
        role=RoleVO(current_user.role.value),
    )

    return CommentResponse.from_dto(dto)


@comment_router.get(
    "/{curriculum_id}/comments",
    response_model=CommentPageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_comments_by_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    comment_service: CommentService = Depends(Provide[Container.comment_service]),
) -> CommentPageResponse:
    """특정 커리큘럼의 댓글 목록 조회"""
    query = CommentQuery(
        curriculum_id=curriculum_id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: CommentPageDTO = await comment_service.get_comments(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return CommentPageResponse.from_dto(page_dto)


@comment_router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_comment_by_id(
    comment_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    comment_service: CommentService = Depends(Provide[Container.comment_service]),
) -> CommentResponse:
    """ID로 댓글 상세 조회"""
    dto: CommentDTO = await comment_service.get_comment_by_id(
        comment_id=comment_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return CommentResponse.from_dto(dto)


@comment_router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_comment(
    comment_id: str,
    request: UpdateCommentRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    comment_service: CommentService = Depends(Provide[Container.comment_service]),
) -> CommentResponse:
    """댓글 수정"""
    command: UpdateCommentCommand = request.to_command(
        comment_id=comment_id,
        user_id=current_user.id,
    )

    dto: CommentDTO = await comment_service.update_comment(
        command=command,
        role=RoleVO(current_user.role.value),
    )

    return CommentResponse.from_dto(dto)


@comment_router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_comment(
    comment_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    comment_service: CommentService = Depends(Provide[Container.comment_service]),
) -> None:
    """댓글 삭제"""
    await comment_service.delete_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )


# 사용자 댓글 관련 엔드포인트
user_comment_router = APIRouter(prefix="/users/me/comments", tags=["User Comments"])


@user_comment_router.get(
    "",
    response_model=CommentPageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_my_comments(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    comment_service: CommentService = Depends(Provide[Container.comment_service]),
) -> CommentPageResponse:
    """내가 작성한 모든 댓글 목록 조회"""
    query = CommentQuery(
        user_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: CommentPageDTO = await comment_service.get_comments(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return CommentPageResponse.from_dto(page_dto)
