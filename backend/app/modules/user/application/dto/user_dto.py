from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.modules.user.domain.entity.user import User
from app.modules.user.domain.vo.role import RoleVO


@dataclass
class CreateUserCommand:
    email: str
    name: str
    password: str


@dataclass
class UpdateUserCommand:
    user_id: str
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleVO] = None


@dataclass
class UserQuery:
    page: int = 1
    items_per_page: int = 10


@dataclass
class UserDTO:
    id: str
    email: str
    name: str
    role: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserDTO":
        """도메인 엔티티에서 DTO 변환"""
        return cls(
            id=user.id,
            email=str(user.email),
            name=str(user.name),
            role=user.role.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@dataclass
class UsersPageDTO:
    """사용자 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    users: list[UserDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        users: list[User],
    ) -> "UsersPageDTO":
        """도메인 엔티티 리스트에서 DTO 변환"""
        user_dtos = [UserDTO.from_domain(user) for user in users]
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            users=user_dtos,
        )
