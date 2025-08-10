from abc import ABCMeta, abstractmethod
from typing import Optional

from app.modules.user.domain.vo import Email, Name
from app.modules.user.domain.entity import User


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, user: User) -> None:
        """save user"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[User]:
        """find user by id"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """find user by email"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_name(self, name: Name) -> Optional[User]:
        """find user by name"""
        raise NotImplementedError

    @abstractmethod
    async def find_users(
        self, page: int, items_per_page: int
    ) -> tuple[int, list[User]]:
        """find users in list (paging)"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> None:
        """update user information"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: str) -> None:
        """delete user"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """check email is exist"""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_name(self, name: Name) -> bool:
        """check name is exist"""
        raise NotImplementedError
