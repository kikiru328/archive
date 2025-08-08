import pytest
from datetime import datetime, timezone
from app.modules.user.application.dto.user_dto import (
    CreateUserCommand,
    UpdateUserCommand,
    UserDTO,
    UsersPageDTO,
)
from app.modules.user.domain.entity.user import User
from app.modules.user.domain.vo import Email, Name, Password, RoleVO


class TestUserDTO:

    @pytest.fixture  # type: ignore
    def sample_user(self) -> User:
        return User(
            id="test_id",
            email=Email("test@example.com"),
            name=Name("testuser"),
            password=Password("hashed_password"),
            role=RoleVO.USER,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
        )

    def test_user_dto_from_domain(self, sample_user: User) -> None:
        """UserDTO test for user dto"""
        # When
        dto = UserDTO.from_domain(sample_user)

        # Then
        assert dto.id == "test_id"
        assert dto.email == "test@example.com"
        assert dto.name == "testuser"
        assert dto.role == "USER"
        assert dto.created_at == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert dto.updated_at == datetime(2024, 1, 2, tzinfo=timezone.utc)

    def test_user_page_dto_from_domain(self, sample_user: User) -> None:
        """UsersPageDTO test for users page dto"""
        # When
        page_dto = UsersPageDTO.from_domain(
            total_count=1,
            page=1,
            items_per_page=10,
            users=[sample_user],
        )

        # Then
        assert page_dto.total_count == 1
        assert page_dto.page == 1
        assert page_dto.items_per_page == 10
        assert len(page_dto.users) == 1
        assert page_dto.users[0].id == "test_id"

    def test_create_user_command(self) -> None:
        """CreateUserCommand create test"""
        # When
        command = CreateUserCommand(
            email="test@example.com", name="testuser", password="Password123!"
        )

        # Then
        assert command.email == "test@example.com"
        assert command.name == "testuser"
        assert command.password == "Password123!"

    def test_update_user_command(self) -> None:
        """UpdateUserCommand create test"""
        # When
        command = UpdateUserCommand(
            user_id="test_id", name="newname", password="NewPassword123!"
        )

        # Then
        assert command.user_id == "test_id"
        assert command.name == "newname"
        assert command.password == "NewPassword123!"
        assert command.role is None
