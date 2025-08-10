import pytest
from app.modules.curriculum.domain.vo.lessons import Lessons
from app.modules.curriculum.domain.vo.lesson import Lesson


class TestLessons:
    """Lessons VO 테스트"""

    def test_valid_lessons_creation(self):
        """정상적인 레슨 목록 생성 테스트"""
        lessons = Lessons(["Python 기초", "변수", "함수"])
        assert lessons.count == 3
        assert lessons.items == ["Python 기초", "변수", "함수"]

    def test_lessons_strip_whitespace(self):
        """공백 제거 테스트"""
        lessons = Lessons(["  Python 기초  ", "변수", "  함수  "])
        assert lessons.items == ["Python 기초", "변수", "함수"]

    def test_lessons_remove_empty(self):
        """빈 문자열 제거 테스트"""
        lessons = Lessons(["Python 기초", "", "  ", "함수"])
        assert lessons.count == 2
        assert lessons.items == ["Python 기초", "함수"]

    def test_lessons_count_boundaries(self):
        """개수 경계값 테스트"""
        # 정상: 최소 1개
        lessons_min = Lessons(["Python 기초"])
        assert lessons_min.count == 1

        # 정상: 최대 5개
        lessons_max = Lessons(["L1", "L2", "L3", "L4", "L5"])
        assert lessons_max.count == 5

        # 비정상: 6개
        with pytest.raises(ValueError, match="Lessons cannot exceed 5 items"):
            Lessons(["L1", "L2", "L3", "L4", "L5", "L6"])

    def test_empty_lessons(self):
        """빈 레슨 목록 테스트"""
        with pytest.raises(ValueError, match="Lessons must have at least 1 item"):
            Lessons([])

        with pytest.raises(ValueError, match="Lessons must have at least 1 item"):
            Lessons(["", "  ", "   "])

    def test_invalid_type(self):
        """잘못된 타입 테스트"""
        with pytest.raises(ValueError, match="Lessons must be a list"):
            Lessons("not a list")  # type: ignore

        with pytest.raises(ValueError, match="Lesson at index 0 must be a string"):
            Lessons([123, "valid"])

    def test_lessons_property(self):
        """lessons 속성 테스트"""
        lessons = Lessons(["Python 기초", "변수"])
        lesson_vos = lessons.lessons

        assert len(lesson_vos) == 2
        assert all(isinstance(lesson, Lesson) for lesson in lesson_vos)
        assert lesson_vos[0].value == "Python 기초"
        assert lesson_vos[1].value == "변수"

    def test_add_lesson(self):
        """레슨 추가 테스트"""
        lessons = Lessons(["Python 기초", "변수"])
        new_lessons = lessons.add_lesson("함수")

        # 원본은 변경되지 않음 (불변성)
        assert lessons.count == 2
        assert lessons.items == ["Python 기초", "변수"]

        # 새 인스턴스는 레슨이 추가됨
        assert new_lessons.count == 3
        assert new_lessons.items == ["Python 기초", "변수", "함수"]

        # 최대 개수 초과 시 에러
        lessons_max = Lessons(["L1", "L2", "L3", "L4", "L5"])
        with pytest.raises(ValueError, match="Cannot add more than 5 lessons"):
            lessons_max.add_lesson("L6")

    def test_remove_lesson_at(self):
        """레슨 제거 테스트"""
        lessons = Lessons(["Python 기초", "변수", "함수"])
        new_lessons = lessons.remove_lesson_at(1)  # "변수" 제거

        # 원본은 변경되지 않음 (불변성)
        assert lessons.count == 3
        assert lessons.items == ["Python 기초", "변수", "함수"]

        # 새 인스턴스는 레슨이 제거됨
        assert new_lessons.count == 2
        assert new_lessons.items == ["Python 기초", "함수"]

        # 잘못된 인덱스
        with pytest.raises(ValueError, match="Index 5 out of range"):
            lessons.remove_lesson_at(5)

        # 최소 개수 미만으로 제거 시도
        lessons_min = Lessons(["Python 기초"])
        with pytest.raises(
            ValueError, match="Cannot remove lesson, minimum 1 required"
        ):
            lessons_min.remove_lesson_at(0)

    def test_update_lesson_at(self):
        """레슨 수정 테스트"""
        lessons = Lessons(["Python 기초", "변수", "함수"])
        new_lessons = lessons.update_lesson_at(1, "데이터 타입")

        # 원본은 변경되지 않음 (불변성)
        assert lessons.count == 3
        assert lessons.items == ["Python 기초", "변수", "함수"]

        # 새 인스턴스는 레슨이 수정됨
        assert new_lessons.count == 3
        assert new_lessons.items == ["Python 기초", "데이터 타입", "함수"]

        # 잘못된 인덱스
        with pytest.raises(ValueError, match="Index 5 out of range"):
            lessons.update_lesson_at(5, "새 레슨")

    def test_lessons_indexing(self):
        """인덱싱 테스트"""
        lessons = Lessons(["Python 기초", "변수", "함수"])

        assert lessons[0].value == "Python 기초"
        assert lessons[1].value == "변수"
        assert lessons[2].value == "함수"

        with pytest.raises(IndexError):
            lessons[3]

    def test_lessons_iteration(self):
        """반복 가능성 테스트"""
        lessons = Lessons(["Python 기초", "변수", "함수"])

        lesson_values = [lesson.value for lesson in lessons]
        assert lesson_values == ["Python 기초", "변수", "함수"]

        # len() 함수 사용 가능
        assert len(lessons) == 3

    def test_lessons_equality(self):
        """동등성 테스트"""
        lessons1 = Lessons(["Python 기초", "변수"])
        lessons2 = Lessons(["Python 기초", "변수"])
        lessons3 = Lessons(["Java 기초", "변수"])

        assert lessons1 == lessons2
        assert lessons1 != lessons3

    def test_lessons_hash(self):
        """해시 테스트"""
        lessons1 = Lessons(["Python 기초", "변수"])
        lessons2 = Lessons(["Python 기초", "변수"])

        assert hash(lessons1) == hash(lessons2)

        # set에서 사용 가능
        lessons_set = {lessons1, lessons2}
        assert len(lessons_set) == 1

    def test_lessons_repr(self):
        """문자열 표현 테스트"""
        lessons = Lessons(["Python 기초", "변수"])
        assert repr(lessons) == "<Lessons ['Python 기초', '변수']>"
