import asyncio
from datetime import datetime, timezone
from typing import Optional
from ulid import ULID  # type: ignore
from app.core.auth import Role, create_access_token
from app.utils.crypto import Crypto

# from app.common.monitoring.metrics import increment_user_registration
from app.modules.user.application.exception import (
    EmailNotFoundError,
    ExistEmailError,
    ExistNameError,
    PasswordIncorrectError,
)
from app.modules.user.domain.vo.password_validator import PasswordValidator
from app.modules.user.application.dto.user_dto import CreateUserCommand, UserDTO
from app.modules.user.domain.repository.user_repo import IUserRepository
from app.modules.user.domain.service.user_domain_service import UserDomainService
from app.modules.user.domain.vo import Email, Name, Password, RoleVO


class AuthService:
    """Authentication Application Service"""

    def __init__(
        self,
        user_repo: IUserRepository,
        user_domain_service: UserDomainService,
        ulid: ULID = ULID(),
        crypto: Crypto = Crypto(),
    ):

        self.user_repo: IUserRepository = user_repo
        self.user_domain_service: UserDomainService = user_domain_service
        self.ulid: ULID = ulid
        self.crypto: Crypto = crypto

    async def signup(
        self,
        command: CreateUserCommand,
        created_at: Optional[datetime] = None,
    ) -> UserDTO:
        """Sign up"""
        created_at = created_at or datetime.now(timezone.utc)

        email = Email(command.email)
        name = Name(command.name)

        if not await self.user_domain_service.is_email_unique(email):
            raise ExistEmailError

        if not await self.user_domain_service.is_name_unique(name):
            raise ExistNameError

        PasswordValidator.validate(command.password)
        hashed: str = await asyncio.to_thread(
            self.crypto.encrypt,
            command.password,
        )

        user = self.user_domain_service.create_user(
            user_id=self.ulid.generate(),
            email=email,
            name=name,
            password=Password(hashed),
            role=RoleVO.USER,
            created_at=created_at,
        )

        await self.user_repo.save(user)
        # increment_user_registration()

        return UserDTO.from_domain(user)

    async def login(self, email: str, password: str) -> tuple[str, str]:
        """Log In"""
        user = await self.user_repo.find_by_email(Email(email))

        if user is None:
            raise EmailNotFoundError("Email Not found")

        if not self.crypto.verify(password, user.password.value):
            raise PasswordIncorrectError("Password incorrect")

        access_token = create_access_token(subject=user.id, role=Role(user.role))
        # increment_user_login()

        return access_token, user.role.value
