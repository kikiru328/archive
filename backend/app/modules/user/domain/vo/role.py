from enum import StrEnum


class RoleVO(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"

    def is_admin(self) -> bool:
        """check user's role is ADMIN"""
        return self == RoleVO.ADMIN

    def is_user(self) -> bool:
        """check user's role is USER"""
        return self == RoleVO.USER
