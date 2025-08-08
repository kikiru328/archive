import pytest
from app.modules.curriculum.domain.vo.lesson import Lesson


class TestLesson:
    """Lesson VO 테스트"""

    def test_valid_lesson_creation(self):
        """정상적인 레슨 생성 테스트"""
        lesson = Lesson("Python 기초 문법")
        assert lesson.value == "Python 기초 문법"
        assert str(lesson) == "Python 기초 문법"

    def test_lesson_strip_whitespace(self):
        """공백 제거 테스트"""
        lesson = Lesson("  변수와 데이터 타입  ")
        assert lesson.value == "변수와 데이터 타입"

    def test_lesson_length_boundaries(self):
        """길이 경계값 테스트"""
        # 정상: 최소 1글자
        lesson_min = Lesson("A")
        assert lesson_min.value == "A"

        # 정상: 최대 100글자
        long_lesson = "a" * 100
        lesson_max = Lesson(long_lesson)
        assert lesson_max.value == long_lesson

        # 비정상: 101글자
        with pytest.raises(ValueError, match="Lesson cannot exceed 100 characters"):
            Lesson("a" * 101)

    def test_empty_lesson(self):
        """빈 레슨 테스트"""
        with pytest.raises(ValueError, match="Lesson cannot be empty"):
            Lesson("")

        with pytest.raises(ValueError, match="Lesson cannot be empty"):
            Lesson("   ")

    def test_invalid_type(self):
        """잘못된 타입 테스트"""
        with pytest.raises(ValueError, match="Lesson must be a string"):
            Lesson(123)  # type: ignore

        with pytest.raises(ValueError, match="Lesson must be a string"):
            Lesson(None)  # type: ignore

    def test_lesson_equality(self):
        """동등성 테스트"""
        lesson1 = Lesson("Python 기초")
        lesson2 = Lesson("Python 기초")
        lesson3 = Lesson("Java 기초")

        assert lesson1 == lesson2
        assert lesson1 != lesson3
        assert lesson1 != "Python 기초"  # 문자열과는 다름

    def test_lesson_hash(self):
        """해시 테스트"""
        lesson1 = Lesson("Python 기초")
        lesson2 = Lesson("Python 기초")

        assert hash(lesson1) == hash(lesson2)

        # set에서 사용 가능
        lesson_set = {lesson1, lesson2}
        assert len(lesson_set) == 1

    def test_lesson_repr(self):
        """문자열 표현 테스트"""
        lesson = Lesson("Python 기초")
        assert repr(lesson) == "<Lesson 'Python 기초'>"
