from datetime import datetime, timezone
from typing import Optional

from app.modules.user.domain.vo import Email, Name, Password, RoleVO
from app.modules.user.domain.entity.user import User
from app.modules.user.domain.repository.user_repo import IUserRepository


class UserDomainService:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo: IUserRepository = user_repo

    async def is_email_unique(self, email: Email) -> bool:
        """Check whether the email is unique (i.e., not already in use)"""
        exists: bool = await self.user_repo.exists_by_email(email)
        return not exists

    async def is_name_unique(
        self, name: Name, exclude_user_id: Optional[str] = None
    ) -> bool:
        """Check whether the name is unique"""
        exists: bool = await self.user_repo.exists_by_name(name)
        if not exists:
            return True

        if exclude_user_id:
            user: User | None = await self.user_repo.find_by_name(name)
            if user and user.id == exclude_user_id:
                return True

        return False

    async def can_update_user(self, user_id: str, name: Optional[Name] = None) -> bool:
        """
        이름을 변경할 때만 고유성 검사.
        - name이 None이면 변경사항이 없으므로 True
        - name이 주어지면 is_name_unique(name, exclude_user_id=user_id) 호출
        """
        if name is None:
            return True
        return await self.is_name_unique(name, exclude_user_id=user_id)

    def create_user(
        self,
        user_id: str,
        email: Email,
        name: Name,
        password: Password,
        role: RoleVO = RoleVO.USER,
        created_at: Optional[datetime] = None,
    ) -> User:
        """사용자 생성 (팩토리 메서드)"""
        now = created_at or datetime.now(timezone.utc)

        return User(
            id=user_id,
            email=email,
            name=name,
            password=password,
            role=role,
            created_at=now,
            updated_at=now,
        )
