from typing import Any, List
from pydantic import BaseModel, Field


class AdminListUsersQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    items_per_page: int = Field(default=10, ge=1, le=100)


class AdminUpdateUserRoleBody(BaseModel):
    role: str  # "USER" | "ADMIN" | ... (서비스에서 검증)


class AdminUserItem(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    role: str = Field(..., description="역할")
    email: str = Field(..., description="이메일")
    name: str = Field(..., description="이름")


class AdminGetUserResponse(AdminUserItem):
    @classmethod
    def from_dto(cls, dto: Any) -> "AdminGetUserResponse":
        role_value = getattr(dto.role, "value", None)
        role_str = role_value if role_value is not None else str(dto.role)
        return cls(
            user_id=getattr(dto, "id"),
            role=role_str,
            email=getattr(dto, "email"),
            name=getattr(dto, "name"),
        )


class AdminGetUsersPageResponse(BaseModel):
    items: List[AdminUserItem]
    total: int
    page: int
    items_per_page: int

    @classmethod
    def from_page_dto(cls, page_dto: Any) -> "AdminGetUsersPageResponse":
        def _get(obj: Any, candidates: list[str], default: Any = None) -> Any:
            for c in candidates:
                if hasattr(obj, c):
                    return getattr(obj, c)
            return default

        # Users 리스트 필드명 호환: items | users | data | results | rows
        users_list = _get(page_dto, ["items", "users", "data", "results", "rows"])
        if users_list is None:
            raise ValueError(
                "UsersPageDTO에서 사용자 리스트 필드를 찾지 못했습니다. (items/users/data/results/rows 중 하나 필요)"
            )

        total = _get(page_dto, ["total", "total_count", "count"], 0)
        page = _get(page_dto, ["page", "current_page", "page_index"], 1)
        items_per_page = _get(
            page_dto, ["items_per_page", "size", "per_page", "limit"], 10
        )

        return cls(
            items=[
                AdminUserItem(
                    user_id=getattr(u, "id"),
                    role=(
                        getattr(getattr(u, "role"), "value", None)
                        or str(getattr(u, "role"))
                    ),
                    email=getattr(u, "email"),
                    name=getattr(u, "name"),
                )
                for u in users_list
            ],
            total=total,
            page=page,
            items_per_page=items_per_page,
        )
