import pytest

from app.modules.user.domain.vo.password_validator import PasswordValidator


class TestPasswordValidator:
    @pytest.mark.parametrize(
        "valid_password",
        [
            "Test123!",
            "MyP@ssw0rd",
            "Str0ng#Pass",
            "C0mpl3x!P@ssw0rd",
        ],
    )
    def test_valid_passwords(self, valid_password) -> None:  # type: ignore
        # Should not raise exception
        PasswordValidator.validate(valid_password)
        assert PasswordValidator.is_valid(valid_password) is True

    @pytest.mark.parametrize(
        "invalid_password,expected_error",
        [
            ("Test1!", "비밀번호는"),  # too short
            ("test123!", "비밀번호는"),  # no uppercase
            ("TEST123!", "비밀번호는"),  # no lowercase
            ("TestABC!", "비밀번호는"),  # no digit
            ("Test123a", "비밀번호는"),  # no special char
            ("Test 123!", "비밀번호는"),  # has space
        ],
    )
    def test_invalid_passwords(self, invalid_password, expected_error):  # type: ignore
        with pytest.raises(ValueError, match=expected_error):
            PasswordValidator.validate(invalid_password)
        assert PasswordValidator.is_valid(invalid_password) is False

    def test_password_too_long(self):
        long_password = "Test123!" + "a" * 60
        with pytest.raises(ValueError, match="비밀번호는"):
            PasswordValidator.validate(long_password)

    def test_non_string_password(self):
        with pytest.raises(ValueError, match="Password must be a string"):
            PasswordValidator.validate(123)  # type: ignore
        assert PasswordValidator.is_valid(123) is False  # type: ignore
