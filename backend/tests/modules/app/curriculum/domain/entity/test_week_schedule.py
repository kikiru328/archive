import pytest

from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.vo.week_number import WeekNumber
from app.modules.curriculum.domain.vo.lessons import Lessons


class TestWeekSchedule:
    """주차 스케줄 엔티티 테스트"""

    def test_week_schedule_creation_success(self):
        """주차 스케줄 생성 성공 테스트"""
        # Given
        week_number = WeekNumber(1)
        lessons = Lessons(["Python 기초", "변수와 자료형"])

        # When
        week_schedule = WeekSchedule(week_number=week_number, lessons=lessons)

        # Then
        assert week_schedule.week_number == week_number
        assert week_schedule.lessons == lessons

    def test_week_schedule_creation_with_invalid_week_number_type_should_fail(self):
        """잘못된 타입의 주차 번호로 생성 시 실패"""
        # Given
        invalid_week_number = 1  # Should be WeekNumber VO
        lessons = Lessons(["Python 기초"])

        # When & Then
        with pytest.raises(TypeError, match="week_number must be WeekNumber"):
            WeekSchedule(week_number=invalid_week_number, lessons=lessons)  # type: ignore

    def test_week_schedule_creation_with_invalid_lessons_type_should_fail(self):
        """잘못된 타입의 레슨으로 생성 시 실패"""
        # Given
        week_number = WeekNumber(1)
        invalid_lessons = ["Python 기초", "변수와 자료형"]  # Should be Lessons VO

        # When & Then
        with pytest.raises(TypeError, match="lessons must be Lessons"):
            WeekSchedule(week_number=week_number, lessons=invalid_lessons)  # type: ignore

    def test_add_lesson_success(self):
        """레슨 추가 성공 테스트 (불변성 유지)"""
        # Given
        week_schedule = self._create_valid_week_schedule()
        new_lesson = "새로운 레슨"

        # When
        updated_week_schedule = week_schedule.add_lesson(new_lesson)

        # Then
        # 원본은 변경되지 않음
        assert len(week_schedule.lessons.items) == 2
        # 새로운 객체는 레슨이 추가됨
        assert len(updated_week_schedule.lessons.items) == 3
        assert new_lesson in updated_week_schedule.lessons.items
        # 주차 번호는 동일
        assert updated_week_schedule.week_number == week_schedule.week_number

    def test_remove_lesson_at_success(self):
        """지정 인덱스 레슨 제거 성공 테스트 (불변성 유지)"""
        # Given
        week_schedule = self._create_valid_week_schedule()

        # When
        updated_week_schedule = week_schedule.remove_lesson_at(0)

        # Then
        # 원본은 변경되지 않음
        assert len(week_schedule.lessons.items) == 2
        # 새로운 객체는 레슨이 제거됨
        assert len(updated_week_schedule.lessons.items) == 1
        assert "Python 기초" not in updated_week_schedule.lessons.items
        assert "변수와 자료형" in updated_week_schedule.lessons.items

    def test_update_lesson_at_success(self):
        """지정 인덱스 레슨 수정 성공 테스트 (불변성 유지)"""
        # Given
        week_schedule = self._create_valid_week_schedule()
        new_lesson = "수정된 레슨"

        # When
        updated_week_schedule = week_schedule.update_lesson_at(0, new_lesson)

        # Then
        # 원본은 변경되지 않음
        assert "Python 기초" in week_schedule.lessons.items
        # 새로운 객체는 레슨이 수정됨
        assert new_lesson in updated_week_schedule.lessons.items
        assert "Python 기초" not in updated_week_schedule.lessons.items
        assert len(updated_week_schedule.lessons.items) == 2

    def test_get_lesson_count(self):
        """레슨 개수 반환 테스트"""
        # Given
        week_schedule = self._create_valid_week_schedule()

        # When
        lesson_count = week_schedule.get_lesson_count()

        # Then
        assert lesson_count == 2

    def test_has_lesson_success(self):
        """특정 레슨 포함 여부 확인 테스트"""
        # Given
        week_schedule = self._create_valid_week_schedule()

        # When & Then
        assert week_schedule.has_lesson("Python 기초")
        assert week_schedule.has_lesson("변수와 자료형")
        assert not week_schedule.has_lesson("존재하지 않는 레슨")

    def test_str_representation(self):
        """문자열 표현 테스트"""
        # Given
        week_schedule = self._create_valid_week_schedule()

        # When
        str_representation = str(week_schedule)

        # Then
        assert "Week 1" in str_representation
        assert "2 lessons" in str_representation

    def test_repr_representation(self):
        """repr 표현 테스트"""
        # Given
        week_schedule = self._create_valid_week_schedule()

        # When
        repr_representation = repr(week_schedule)

        # Then
        assert "<WeekSchedule" in repr_representation
        assert "week=1" in repr_representation
        assert "lessons_count=2" in repr_representation

    def test_immutability_through_methods(self):
        """메서드를 통한 불변성 보장 테스트"""
        # Given
        original_week_schedule = self._create_valid_week_schedule()
        original_lessons = original_week_schedule.lessons.items.copy()

        # When - 여러 메서드 호출
        updated1 = original_week_schedule.add_lesson("새 레슨")
        updated2 = original_week_schedule.remove_lesson_at(0)
        updated3 = original_week_schedule.update_lesson_at(1, "수정된 레슨")

        # Then - 원본은 변경되지 않음
        assert original_week_schedule.lessons.items == original_lessons

        # 각각의 새로운 객체는 올바르게 변경됨
        assert len(updated1.lessons.items) == 3
        assert len(updated2.lessons.items) == 1
        assert "수정된 레슨" in updated3.lessons.items

    def _create_valid_week_schedule(self) -> WeekSchedule:
        """유효한 주차 스케줄 생성 헬퍼 메서드"""
        return WeekSchedule(
            week_number=WeekNumber(1), lessons=Lessons(["Python 기초", "변수와 자료형"])
        )
