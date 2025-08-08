import pytest

from app.modules.user.domain.vo import Name


class TestName:
    @pytest.mark.parametrize(
        "valid_name",
        [
            "test",
            "testuser",
            "테스트",
            "test123",
            "한글123",
            "TestUser",
            "test user",
        ],
    )
    def test_valid_names(self, valid_name) -> None:  # type: ignore
        name = Name(valid_name)
        assert str(name) == valid_name
        assert name.value == valid_name

    def test_name_strip_whitespace(self):
        name = Name("  testuser  ")
        assert str(name) == "testuser"

    @pytest.mark.parametrize("short_name", ["", " ", "a"])
    def test_name_too_short(self, short_name):  # type: ignore
        with pytest.raises(
            ValueError, match="Name length must be between|Name cannot be empty"
        ):
            Name(short_name)

    def test_name_too_long(self):
        long_name = "a" * 33
        with pytest.raises(ValueError, match="Name length must be between"):
            Name(long_name)

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "test@user",
            "test-user",
            "test_user",
            "test!",
            "test.user",
        ],
    )
    def test_invalid_name_characters(self, invalid_name) -> None:  # type: ignore
        with pytest.raises(ValueError, match="Name can only contain"):
            Name(invalid_name)

    def test_non_string_name(self):
        with pytest.raises(ValueError, match="Name must be a string"):
            Name(123)  # pyright: ignore[reportArgumentType]

    def test_name_equality(self):
        name1 = Name("testuser")
        name2 = Name("testuser")
        name3 = Name("otheruser")

        assert name1 == name2
        assert name1 != name3
        assert name1 != "testuser"  # 다른 타입과 비교
