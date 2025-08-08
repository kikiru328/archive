from datetime import datetime, timezone
from typing import Optional

import pytest
import pytest_asyncio
from app.modules.user.domain.entity.user import User
from app.modules.user.domain.vo import Email, Name, Password, RoleVO
from app.modules.user.domain.repository.user_repo import IUserRepository
from app.modules.user.domain.service.user_domain_service import UserDomainService


class InMemoryUserRepository(IUserRepository):
    """Inmemory repository for Test"""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._email_index: dict[str, str] = {}
        self._name_index: dict[str, str] = {}

    async def save(self, user: User) -> None:
        self._users[user.id] = user
        self._email_index[str(user.email)] = user.id
        self._name_index[str(user.name)] = user.id

    async def find_by_id(self, id: str) -> Optional[User]:
        return self._users.get(id)

    async def find_by_email(self, email: Email) -> Optional[User]:
        user_id: str | None = self._email_index.get(str(email))
        return self._users.get(user_id) if user_id else None

    async def find_by_name(self, name: Name) -> Optional[User]:
        user_id = self._name_index.get(str(name))
        return self._users.get(user_id) if user_id else None

    # 나머지 메서드들은 테스트에 필요하지 않으므로 생략
    async def find_users(
        self, page: int, items_per_page: int
    ) -> tuple[int, list[User]]:
        total = len(self._users)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        users_slice = list(self._users.values())[start:end]
        return total, users_slice

    async def update(self, user: User) -> None:
        pass

    async def delete(self, id: str) -> None:
        pass

    async def exists_by_email(self, email: Email) -> bool:
        return str(email) in self._email_index

    async def exists_by_name(self, name: Name) -> bool:  # type: ignore
        return str(name) in self._name_index


class TestUserDomainService:
    @pytest_asyncio.fixture()  # type: ignore
    async def user_repo(self) -> InMemoryUserRepository:
        """Dependency as Mock"""
        return InMemoryUserRepository()

    @pytest_asyncio.fixture()
    async def user_domain_service(
        self, user_repo: InMemoryUserRepository
    ) -> UserDomainService:
        """Dependency as Mock"""
        return UserDomainService(user_repo)

    @pytest_asyncio.fixture()
    async def existing_user(self, user_repo: InMemoryUserRepository) -> User:
        """create user in repo (mock)"""
        user = User(
            id="01HZKTM7K2QXYZ1ABCDEF01234",
            email=Email("existing@example.com"),
            name=Name("existing"),
            password=Password("hashed_password"),
            role=RoleVO.USER,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await user_repo.save(user)
        return user

    @pytest.mark.asyncio
    async def test_is_email_unique_when_new_email(
        self, user_domain_service: UserDomainService
    ) -> None:
        # Given
        email = Email("new@example.com")

        # When: email이 unique (True)
        result: bool = await user_domain_service.is_email_unique(email)

        # Then
        assert result > 0

    @pytest.mark.asyncio
    async def test_is_email_unique_when_existing_email(
        self, user_domain_service: UserDomainService, existing_user: User
    ) -> None:
        # Given
        email = Email("existing@example.com")

        # When: Email이 이미 존재하는지 (False)
        result: bool = await user_domain_service.is_email_unique(email)

        # Then
        assert result is False

    @pytest.mark.asyncio
    async def test_is_name_unique_when_new_name(
        self, user_domain_service: UserDomainService
    ) -> None:
        # Given
        name = Name("newname")

        # When: Name이 unique (True)
        result: bool = await user_domain_service.is_name_unique(name)

        # Then
        assert result is True

    @pytest.mark.asyncio
    async def test_is_name_unique_when_existing_name(
        self, user_domain_service: UserDomainService, existing_user: User
    ) -> None:
        # Given
        name = Name("existing")

        # When: Name이 이미 존재하는 지
        result: bool = await user_domain_service.is_name_unique(name)

        # Then
        assert result is False

    @pytest.mark.asyncio
    async def test_is_name_unique_exclude_self(
        self, user_domain_service: UserDomainService, existing_user: User
    ) -> None:
        # Given
        name = Name("existing")

        # When: 나 자신인지
        result: bool = await user_domain_service.is_name_unique(
            name, exclude_user_id=existing_user.id
        )

        # Then
        assert result is True

    @pytest.mark.asyncio
    async def test_is_name_unique_exclude_different_user(
        self, user_domain_service: UserDomainService, existing_user: User
    ) -> None:
        # Given
        name = Name("existing")
        different_user_id = "01HZKTM7K2QXYZ1ABCDEF99999"

        # When: 다른사람의 name과 비교
        result: bool = await user_domain_service.is_name_unique(
            name, exclude_user_id=different_user_id
        )

        # Then
        assert result is False

    def test_create_user_with_default_role(
        self,
        user_domain_service: UserDomainService,
    ) -> None:
        # Given
        user_id = "01HZKTM7K2QXYZ1ABCDEF01234"
        email = Email("test@example.com")
        name = Name("testuser")
        password = Password("hashed_password")

        # When
        user: User = user_domain_service.create_user(user_id, email, name, password)

        # Then
        assert user.id == user_id
        assert user.email == email
        assert user.name == name
        assert user.password == password
        assert user.role == RoleVO.USER
        assert isinstance(user.created_at, datetime)
        assert user.created_at == user.updated_at

    def test_create_user_with_admin_role(
        self,
        user_domain_service: UserDomainService,
    ) -> None:
        # Given
        user_id = "01HZKTM7K2QXYZ1ABCDEF01234"
        email = Email("admin@example.com")
        name = Name("admin")
        password = Password("hashed_password")
        custom_time = datetime.now(timezone.utc)

        # When
        user: User = user_domain_service.create_user(
            user_id, email, name, password, role=RoleVO.ADMIN, created_at=custom_time
        )

        # Then
        assert user.role == RoleVO.ADMIN
        assert user.created_at == custom_time

    @pytest.mark.asyncio
    async def test_can_update_user_without_name_change(
        self, user_domain_service: UserDomainService
    ) -> None:
        # Given
        user_id = "01HZKTM7K2QXYZ1ABCDEF01234"

        # When: 이름 말고 다른 change?
        result: bool = await user_domain_service.can_update_user(user_id)

        # Then
        assert result is True

    @pytest.mark.asyncio
    async def test_can_update_user_with_unique_name(
        self, user_domain_service: UserDomainService
    ) -> None:
        # Given
        user_id = "01HZKTM7K2QXYZ1ABCDEF01234"
        new_name = Name("uniquename")

        # When: 해당 이름으로 변경이 가능한지? (중복검사 후)
        result: bool = await user_domain_service.can_update_user(user_id, new_name)

        # Then
        assert result is True

    @pytest.mark.asyncio
    async def test_can_update_user_with_duplicate_name(
        self, user_domain_service: UserDomainService, existing_user: User
    ) -> None:
        # Given
        different_user_id = "01HZKTM7K2QXYZ1ABCDEF99999"
        existing_name = Name("existing")

        # When: 해당 이름으로 변경이 가능한지? (중복검사 후 X)
        result: bool = await user_domain_service.can_update_user(
            different_user_id, existing_name
        )

        # Then
        assert result is False
