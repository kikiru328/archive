from typing import Annotated
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide
from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.user.application.dto.user_dto import UpdateUserCommand, UserQuery
from app.modules.user.application.service.user_service import UserService
from app.modules.user.interface.schema.user_schema import (
    GetUserResponse,
    GetUsersPageResponse,
    UpdateUserBody,
    UpdateUserResponse,
)


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/me", response_model=GetUserResponse)
@inject
async def get_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUserResponse:
    """현재 로그인한 사용자 정보 조회"""
    user_dto = await user_service.get_user_by_id(current_user.id)
    return GetUserResponse.from_dto(user_dto)


@user_router.put("/me", response_model=UpdateUserResponse)
@inject
async def update_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UpdateUserResponse:
    """현재 로그인한 사용자 정보 수정"""
    command = UpdateUserCommand(
        user_id=current_user.id,
        name=body.name,
        password=body.password,
    )
    user_dto = await user_service.update_user(command)
    return UpdateUserResponse.from_dto(user_dto)


@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> None:
    """현재 로그인한 사용자 계정 삭제"""
    await user_service.delete_user(current_user.id)


@user_router.get("", response_model=GetUsersPageResponse)
@inject
async def get_users_for_social(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 18,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUsersPageResponse:
    """사용자 목록 조회 (소셜 기능용)"""
    query = UserQuery(page=page, items_per_page=items_per_page)
    users_page_dto = await user_service.get_users(query)
    return GetUsersPageResponse.from_dto(users_page_dto)


@user_router.get("/{user_name}", response_model=GetUserResponse)
@inject
async def get_user_by_name(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_name: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUserResponse:
    """사용자명으로 사용자 정보 조회"""
    user_dto = await user_service.get_user_by_name(user_name)
    return GetUserResponse.from_dto(user_dto)
