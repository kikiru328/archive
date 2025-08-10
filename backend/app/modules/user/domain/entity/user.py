from datetime import datetime
from attr import dataclass

from app.modules.user.domain.vo import Email, Name, Password, RoleVO


@dataclass
class User:
    id: str
    email: Email
    name: Name
    password: Password
    role: RoleVO
    created_at: datetime
    updated_at: datetime

    # domain busniness functions

    def update_name(self, new_name: Name, updated_at: datetime) -> None:
        """change user's name"""
        self.name = new_name
        self.update_at: datetime = updated_at

    def update_password(self, new_password: Password, updated_at: datetime) -> None:
        """change user's password"""
        self.password = new_password
        self.update_at: datetime = updated_at  # type: ignore

    def update_role(self, new_role: RoleVO, updated_at: datetime) -> None:
        """change user's role"""
        self.role = new_role
        self.updated_at: datetime = updated_at  # type: ignore

    def is_admin(self) -> bool:
        """Check authorization of ADMIN"""
        return self.role == RoleVO.ADMIN
