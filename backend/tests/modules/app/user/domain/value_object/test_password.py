import pytest

from app.modules.user.domain.vo import Password


class TestPassword:
    def test_valid_password(self):
        hashed = "hashed_password_string"
        password = Password(hashed)
        assert password.value == hashed

    def test_password_str_hidden(self):
        password = Password("hashed_password")
        assert str(password) == "****"

    def test_password_repr_hidden(self):
        password = Password("hashed_password")
        assert repr(password) == "<Password ****>"

    @pytest.mark.parametrize(
        "invalid_password",
        [
            "",
            "   ",
            None,
        ],
    )
    def test_invalid_password(self, invalid_password) -> None:  # type: ignore
        with pytest.raises(
            ValueError, match="Hashed password must be a non-empty string"
        ):
            Password(invalid_password)

    def test_non_string_password(self):
        with pytest.raises(
            ValueError, match="Hashed password must be a non-empty string"
        ):
            Password(123)  # type: ignore

    def test_password_equality(self):
        password1 = Password("hashed1")
        password2 = Password("hashed1")
        password3 = Password("hashed2")

        assert password1 == password2
        assert password1 != password3
        assert password1 != "hashed1"  # 다른 타입과 비교
