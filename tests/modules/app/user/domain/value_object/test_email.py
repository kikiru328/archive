import pytest
from app.modules.user.domain.vo import Email


class TestEmail:
    def test_valid_email(self):
        email = Email("test@example.com")
        assert str(email) == "test@example.com"
        assert email.value == "test@example.com"

    def test_email_normalization(self):
        email = Email("  TeSt@ExAmPlE.CoM  ")
        assert str(email) == "test@example.com"

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
        ],
    )
    def test_invalid_email_format(self, invalid_email):  # type: ignore
        with pytest.raises(ValueError, match="Invalid email format"):
            Email(invalid_email)

    def test_empty_email(self):
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")

    def test_non_string_email(self):
        with pytest.raises(ValueError, match="Email must be a string"):
            Email(123)  # pyright: ignore[reportArgumentType]

    def test_email_equality(self):
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3
        assert email1 != "test@example.com"  # 다른 타입과 비교

    def test_email_hash(self):
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")

        assert hash(email1) == hash(email2)

        # Set에서 사용 가능한지 확인
        email_set = {email1, email2}
        assert len(email_set) == 1
