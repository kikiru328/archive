from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, Field

from app.modules.user.application.dto.user_dto import UserDTO, UsersPageDTO
from app.modules.user.domain.vo.role import RoleVO


class GetUserResponse(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)

    @classmethod
    def from_dto(cls, user_dto: UserDTO) -> "GetUserResponse":
        return cls(
            name=user_dto.name,
            email=user_dto.email,
        )


class UpdateUserBody(BaseModel):
    name: str | None = None
    password: str | None = None


class UpdateUserResponse(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    updated_at: datetime

    @classmethod
    def from_dto(cls, user_dto: UserDTO) -> "UpdateUserResponse":
        return cls(
            name=user_dto.name,
            email=user_dto.email,
            updated_at=user_dto.updated_at,
        )


class GetUsersPageResponse(BaseModel):
    total_count: int
    page: int
    items_per_page: int
    users: List[GetUserResponse]

    @classmethod
    def from_dto(cls, users_page_dto: UsersPageDTO) -> "GetUsersPageResponse":
        users = [GetUserResponse.from_dto(user) for user in users_page_dto.users]
        return cls(
            total_count=users_page_dto.total_count,
            page=users_page_dto.page,
            items_per_page=users_page_dto.items_per_page,
            users=users,
        )


class UpdateUserRoleBody(BaseModel):
    role: RoleVO
