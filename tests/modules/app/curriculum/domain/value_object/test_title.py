import pytest
from app.modules.curriculum.domain.vo.title import Title


class TestTitle:

    def test_valid_title_creation(self):
        title = Title("Python 기초 과정")
        assert title.value == "Python 기초 과정"
        assert str(title) == "Python 기초 과정"

    def test_title_strip_whitespace(self):
        title = Title("  React 웹 개발  ")
        assert title.value == "React 웹 개발"

    def test_title_min_length(self):
        title = Title("AI")
        assert title.value == "AI"

        # 비정상: 1글자
        with pytest.raises(ValueError, match="Title length must be between 2 and 50"):
            Title("A")

    def test_title_max_length(self):
        # 정상: 50글자
        long_title = "a" * 50
        title = Title(long_title)
        assert title.value == long_title

        # 비정상: 51글자
        with pytest.raises(ValueError, match="Title length must be between 2 and 50"):
            Title("a" * 51)

    def test_empty_title(self):
        """빈 제목 테스트"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Title("")

        with pytest.raises(ValueError, match="Title cannot be empty"):
            Title("   ")

    def test_invalid_type(self):
        """잘못된 타입 테스트"""
        with pytest.raises(ValueError, match="Titie must be string"):
            Title(123)  # type: ignore

        with pytest.raises(ValueError, match="Titie must be string"):
            Title(None)  # type: ignore

    def test_title_equality(self):
        """동등성 테스트"""
        title1 = Title("Python 기초")
        title2 = Title("Python 기초")
        title3 = Title("Java 기초")

        assert title1 == title2
        assert title1 != title3
        assert title1 != "Python 기초"  # 문자열과는 다름

    def test_title_hash(self):
        """해시 테스트"""
        title1 = Title("Python 기초")
        title2 = Title("Python 기초")

        assert hash(title1) == hash(title2)

        # set에서 사용 가능
        title_set = {title1, title2}
        assert len(title_set) == 1

    def test_title_repr(self):
        """문자열 표현 테스트"""
        title = Title("Python 기초")
        assert repr(title) == "<Title 'Python 기초'>"
