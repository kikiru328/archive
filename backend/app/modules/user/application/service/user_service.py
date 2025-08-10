from datetime import datetime, timezone
import asyncio
from ulid import ULID  # type: ignore
from app.modules.user.application.dto.user_dto import (
    UpdateUserCommand,
    UserDTO,
    UsersPageDTO,
    UserQuery,
)
from app.modules.user.application.exception import ExistNameError, UserNotFoundError
from app.modules.user.domain.entity.user import User
from app.modules.user.domain.repository.user_repo import IUserRepository
from app.modules.user.domain.service.user_domain_service import UserDomainService
from app.modules.user.domain.vo import Name, Password
from app.modules.user.domain.vo.password_validator import PasswordValidator
from app.utils.crypto import Crypto


class UserService:
    """Application service for User"""

    def __init__(
        self,
        user_repo: IUserRepository,
        user_domain_service: UserDomainService,
        ulid: ULID = ULID(),
        crypto: Crypto = Crypto(),
    ) -> None:

        self.user_repo: IUserRepository = user_repo
        self.user_domain_service: UserDomainService = user_domain_service
        self.ulid: ULID = ulid
        self.crypto: Crypto = crypto

    async def get_user_by_id(self, user_id: str) -> UserDTO:
        """Get User by id"""
        user: User | None = await self.user_repo.find_by_id(id=user_id)
        if user is None:
            raise UserNotFoundError(f"user with id={user_id} not found")
        return UserDTO.from_domain(user)

    async def get_user_by_name(self, user_name: str) -> UserDTO:
        """Get User by name"""
        user: User | None = await self.user_repo.find_by_name(name=Name(user_name))
        if user is None:
            raise UserNotFoundError(f"{user_name} not found")
        return UserDTO.from_domain(user)

    async def update_user(self, command: UpdateUserCommand) -> UserDTO:
        user: User | None = await self.user_repo.find_by_id(command.user_id)
        if user is None:
            raise UserNotFoundError(f"{command.user_id} user not found")

        updated_at = datetime.now(timezone.utc)

        if command.name:
            new_name = Name(command.name)
            if not await self.user_domain_service.is_name_unique(
                new_name, command.user_id
            ):
                raise ExistNameError("Username already exist")
            user.update_name(new_name, updated_at)

        if command.password:
            PasswordValidator.validate(command.password)
            new_hashed_password: str = await asyncio.to_thread(
                self.crypto.encrypt,
                command.password,
            )
            user.update_password(Password(new_hashed_password), updated_at)

        if command.role:
            user.update_role(command.role, updated_at)

        await self.user_repo.update(user)
        return UserDTO.from_domain(user)

    async def get_users(self, query: UserQuery) -> UsersPageDTO:
        """User List by Paging"""
        total_count, users = await self.user_repo.find_users(
            query.page,
            query.items_per_page,
        )
        return UsersPageDTO.from_domain(
            total_count=total_count,
            page=query.page,
            items_per_page=query.items_per_page,
            users=users,
        )

    async def delete_user(self, user_id: str) -> None:
        """delete user"""
        user = await self.user_repo.find_by_id(id=user_id)
        if user is None:
            raise UserNotFoundError(f"user with id={user_id} not found")
        await self.user_repo.delete(id=user_id)

    async def check_user_exists(self, user_id: str) -> bool:
        """check user exists"""
        user = await self.user_repo.find_by_id(user_id)
        return user is not None
