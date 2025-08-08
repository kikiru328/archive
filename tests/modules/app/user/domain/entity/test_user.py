from datetime import datetime, timezone
import pytest

from app.modules.user.domain.vo import Email, Name, Password, RoleVO
from app.modules.user.domain.entity.user import User


@pytest.fixture()  # type: ignore
def user() -> User:
    return User(
        id="01HZKTM7K2QXYZ1ABCDEF01234",
        email=Email("test@example.com"),
        name=Name("testuser"),
        password=Password("hashed_password"),
        role=RoleVO.USER,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class TestUser:

    def test_user_creation(self, user: User) -> None:
        assert user.id == "01HZKTM7K2QXYZ1ABCDEF01234"
        assert str(user.email) == "test@example.com"
        assert str(user.name) == "testuser"
        assert user.role == RoleVO.USER

    def test_update_name(self, user: User) -> None:
        new_name = Name("newname")
        updated_at = datetime.now(timezone.utc)

        user.update_name(new_name, updated_at)

        assert user.name == new_name
        assert user.updated_at == updated_at

    def test_update_password(self, user: User) -> None:
        new_password = Password("new_hashed_password")
        updated_at: datetime = datetime.now(timezone.utc)

        user.update_password(new_password, updated_at)

        assert user.password == new_password
        assert user.updated_at == updated_at

    def test_update_role(self, user: User) -> None:
        updated_at = datetime.now(timezone.utc)

        user.update_role(RoleVO.ADMIN, updated_at)

        assert user.role == RoleVO.ADMIN
        assert user.updated_at == updated_at

    def test_is_admin_false(self, user: User) -> None:
        assert not user.is_admin()

    def test_is_admin_true(self, user: User) -> None:
        user.role = RoleVO.ADMIN
        assert user.is_admin()
