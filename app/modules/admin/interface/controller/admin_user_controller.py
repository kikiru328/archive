# app/modules/admin/interface/controller/admin_user_controller.py
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.auth import assert_admin
from app.core.di_container import Container

from app.modules.user.application.dto.user_dto import UserQuery, UpdateUserCommand
from app.modules.user.application.service.user_service import UserService
from app.modules.user.domain.vo import RoleVO  # 역할 매핑

from app.modules.admin.interface.schema.admin_user_schema import (
    AdminListUsersQuery,
    AdminUpdateUserRoleBody,
    AdminGetUsersPageResponse,
    AdminGetUserResponse,
)

admin_user_router = APIRouter(prefix="/admin/users", tags=["Admin"])


@admin_user_router.get(
    "", response_model=AdminGetUsersPageResponse, status_code=status.HTTP_200_OK
)
@inject
async def list_users(
    query: Annotated[AdminListUsersQuery, Depends()],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> AdminGetUsersPageResponse:
    assert_admin(current_user)
    user_query = UserQuery(page=query.page, items_per_page=query.items_per_page)
    page_dto = await user_service.get_users(user_query)
    return AdminGetUsersPageResponse.from_page_dto(page_dto)


@admin_user_router.get(
    "/{user_id}", response_model=AdminGetUserResponse, status_code=status.HTTP_200_OK
)
@inject
async def get_user(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> AdminGetUserResponse:
    assert_admin(current_user)
    dto = await user_service.get_user_by_id(user_id)
    return AdminGetUserResponse.from_dto(dto)


@admin_user_router.patch(
    "/{user_id}/role",
    response_model=AdminGetUserResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def change_role(
    user_id: str,
    body: AdminUpdateUserRoleBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> AdminGetUserResponse:
    assert_admin(current_user)
    try:
        new_role = RoleVO(body.role)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"invalid role: {body.role}")

    cmd = UpdateUserCommand(user_id=user_id, role=new_role)
    updated = await user_service.update_user(cmd)  # 또는 update_user(cmd)
    return AdminGetUserResponse.from_dto(updated)
