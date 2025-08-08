from typing import Tuple
from unittest.mock import AsyncMock, Mock
import pytest
from ulid import ULID  # type: ignore
from datetime import datetime, timezone
from pytest_mock import MockerFixture

from app.modules.user.application.dto.user_dto import (
    UpdateUserCommand,
    UserDTO,
    UsersPageDTO,
    UserQuery,
)
from app.modules.user.application.exception import ExistNameError, UserNotFoundError
from app.modules.user.application.service.user_service import UserService
from app.modules.user.domain.entity.user import User
from app.modules.user.domain.vo import Email, Name, Password, RoleVO


class TestUserService:

    @pytest.fixture()  # type: ignore
    def user_service(self, mocker: MockerFixture) -> tuple[
        UserService,
        AsyncMock,
        AsyncMock,
        Mock,
    ]:
        mock_user_repo: AsyncMock = mocker.AsyncMock()
        mock_user_domain_service: AsyncMock = mocker.AsyncMock()
        _mock_crypto: Mock = mocker.Mock()
        _mock_crypto.encrypt.return_value = "hashed_password"

        return (
            UserService(
                user_repo=mock_user_repo,
                user_domain_service=mock_user_domain_service,
                ulid=ULID(),
                crypto=_mock_crypto,
            ),
            mock_user_repo,
            mock_user_domain_service,
            _mock_crypto,
        )

    @pytest.fixture()  # type: ignore
    def sample_user(self) -> User:
        return User(
            id="test_id",
            email=Email("test@example.com"),
            name=Name("testuser"),
            password=Password("hashed_password"),
            role=RoleVO.USER,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def test_get_user_by_id_success(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
    ) -> None:
        """get user id in sucess"""
        # Given
        service, mock_user_repo, _, _ = user_service
        mock_user_repo.find_by_id.return_value = sample_user

        # When
        result = await service.get_user_by_id("test_id")

        # Then
        assert isinstance(result, UserDTO)
        assert result.id == "test_id"
        assert result.email == "test@example.com"
        mock_user_repo.find_by_id.assert_called_once_with(id="test_id")

    async def test_get_user_by_id_not_found(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
    ) -> None:
        """get user id in failed, User Not Found"""
        # Given
        service, mock_user_repo, _, _ = user_service
        mock_user_repo.find_by_id.return_value = None

        # When & Then
        with pytest.raises(UserNotFoundError):
            await service.get_user_by_id("non_existent_id")

    async def test_get_user_by_name_success(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
    ) -> None:
        """get user name in success"""
        # Given
        service, mock_user_repo, _, _ = user_service
        mock_user_repo.find_by_name.return_value = sample_user

        # When
        result: UserDTO = await service.get_user_by_name("testuser")

        # Then
        assert isinstance(result, UserDTO)
        assert result.name == "testuser"
        mock_user_repo.find_by_name.assert_called_once()

    async def test_update_user_name_success(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
        mocker: MockerFixture,
    ) -> None:
        """update user name in success"""
        # Given
        service, mock_user_repo, mock_user_domain_service, _ = user_service
        command = UpdateUserCommand(user_id="test_id", name="newname")
        mock_user_repo.find_by_id.return_value = sample_user
        mock_user_domain_service.is_name_unique.return_value = True

        # anyio.to_thread.run_sync 모킹
        mocker.patch("anyio.to_thread.run_sync", return_value="hashed_password")

        # When
        result = await service.update_user(command)

        # Then
        assert result.name == "newname"
        mock_user_domain_service.is_name_unique.assert_called_once()
        mock_user_repo.update.assert_called_once()

    async def test_update_user_name_already_exists(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
    ) -> None:
        """update user name in failed, already exists"""
        # Given
        service, mock_user_repo, mock_user_domain_service, _ = user_service
        command = UpdateUserCommand(user_id="test_id", name="existingname")
        mock_user_repo.find_by_id.return_value = sample_user
        mock_user_domain_service.is_name_unique.return_value = False

        # When & Then
        with pytest.raises(ExistNameError):
            await service.update_user(command)

    async def test_update_user_password_success(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
        mocker: MockerFixture,
    ) -> None:
        """update user password in success"""
        # Given
        service, mock_user_repo, _, _mock_crypto = user_service
        command = UpdateUserCommand(user_id="test_id", password="NewPassword123!")
        mock_user_repo.find_by_id.return_value = sample_user

        # anyio.to_thread.run_sync 모킹
        mocker.patch("anyio.to_thread.run_sync", return_value="new_hashed_password")

        # When
        _result: UserDTO = await service.update_user(command)

        # Then
        mock_user_repo.update.assert_called_once()

    async def test_update_user_not_found(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
    ) -> None:
        """update user in failed, user not found"""
        # Given
        service, mock_user_repo, _, _ = user_service
        command = UpdateUserCommand(user_id="non_existent_id", name="newname")
        mock_user_repo.find_by_id.return_value = None

        # When & Then
        with pytest.raises(UserNotFoundError):
            await service.update_user(command)

    async def test_get_users_success(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
    ) -> None:
        """get user list in success"""
        # Given
        service, mock_user_repo, _, _ = user_service
        query: UserQuery = UserQuery(page=1, items_per_page=10)
        mock_user_repo.find_users.return_value = (1, [sample_user])

        # When
        result: UsersPageDTO = await service.get_users(query)

        # Then
        assert result.total_count == 1
        assert len(result.users) == 1
        assert result.page == 1
        mock_user_repo.find_users.assert_called_once_with(1, 10)

    async def test_delete_user_success(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
    ) -> None:
        """delete user in success"""
        # Given
        service, mock_user_repo, _, _ = user_service
        mock_user_repo.find_by_id.return_value = sample_user

        # When
        await service.delete_user("test_id")

        # Then
        mock_user_repo.delete.assert_called_once_with(id="test_id")

    async def test_delete_user_not_found(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
    ) -> None:
        """delete user in failed - user not found"""
        # Given
        service, mock_user_repo, _, _ = user_service
        mock_user_repo.find_by_id.return_value = None

        # When & Then
        with pytest.raises(UserNotFoundError):
            await service.delete_user("non_existent_id")

    async def test_check_user_exists_true(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
        sample_user: User,
    ) -> None:
        """check user exist => exist"""
        # Given
        service, mock_user_repo, _, _ = user_service
        mock_user_repo.find_by_id.return_value = sample_user

        # When
        result = await service.check_user_exists("test_id")

        # Then
        assert result is True

    async def test_check_user_exists_false(
        self,
        user_service: Tuple[UserService, AsyncMock, AsyncMock, Mock],
    ) -> None:
        """check user exist => not exist"""
        # Given
        service, mock_user_repo, _, _ = user_service
        mock_user_repo.find_by_id.return_value = None

        # When
        result: bool = await service.check_user_exists("non_existent_id")

        # Then
        assert result is False
