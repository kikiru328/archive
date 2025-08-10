import pytest
from app.modules.curriculum.domain.vo.week_number import WeekNumber


class TestWeekNumber:

    def test_valid_week_number(self):
        week = WeekNumber(1)
        assert week.value == 1

        week = WeekNumber(24)
        assert week.value == 24

    def test_week_number_boundaries(self):
        # 정상: 최소값
        week_min = WeekNumber(1)
        assert week_min.value == 1

        # 정상: 최대값
        week_max = WeekNumber(24)
        assert week_max.value == 24

        # 비정상: 범위 벗어남
        with pytest.raises(ValueError, match="WeekNumber must be between 1 and 24"):
            WeekNumber(0)

        with pytest.raises(ValueError, match="WeekNumber must be between 1 and 24"):
            WeekNumber(25)

    def test_invalid_type(self):
        """잘못된 타입 테스트"""
        with pytest.raises(ValueError, match="WeekNumber must be an integer"):
            WeekNumber("1")  # type: ignore

        with pytest.raises(ValueError, match="WeekNumber must be an integer"):
            WeekNumber(1.5)  # type: ignore

    def test_next_week(self):
        """다음 주차 테스트"""
        week1 = WeekNumber(1)
        week2 = week1.next()
        assert week2.value == 2

        # 최대값에서 next() 호출 시 에러
        week_max = WeekNumber(24)
        with pytest.raises(ValueError, match="Cannot get next week beyond maximum"):
            week_max.next()

    def test_previous_week(self):
        """이전 주차 테스트"""
        week2 = WeekNumber(2)
        week1 = week2.previous()
        assert week1.value == 1

        # 최소값에서 previous() 호출 시 에러
        week_min = WeekNumber(1)
        with pytest.raises(ValueError, match="Cannot get previous week below minimum"):
            week_min.previous()

    def test_week_number_comparison(self):
        """주차 번호 비교 테스트"""
        week1 = WeekNumber(1)
        week2 = WeekNumber(2)
        week1_copy = WeekNumber(1)

        # 동등성
        assert week1 == week1_copy
        assert week1 != week2

        # 크기 비교
        assert week1 < week2
        assert week1 <= week2
        assert week1 <= week1_copy
        assert week2 > week1
        assert week2 >= week1
        assert week1 >= week1_copy

    def test_week_number_hash(self):
        """해시 테스트"""
        week1 = WeekNumber(1)
        week1_copy = WeekNumber(1)

        assert hash(week1) == hash(week1_copy)

        # set에서 사용 가능
        week_set = {week1, week1_copy}
        assert len(week_set) == 1

    def test_week_number_repr(self):
        """문자열 표현 테스트"""
        week = WeekNumber(5)
        assert repr(week) == "<WeekNumber 5>"
