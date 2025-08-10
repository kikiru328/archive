import pytest
from app.modules.curriculum.domain.vo.title import Title
from app.modules.curriculum.domain.vo.lessons import Lessons
from app.modules.curriculum.domain.vo.week_number import WeekNumber


@pytest.fixture
def sample_title():
    """테스트용 샘플 Title"""

    return Title("Python 웹 개발 완전 정복")


@pytest.fixture
def sample_lessons():
    """테스트용 샘플 Lessons"""

    return Lessons(
        ["Python 기초 문법", "변수와 데이터 타입", "조건문과 반복문", "함수 정의하기"]
    )


@pytest.fixture
def sample_week_numbers():
    """테스트용 샘플 WeekNumber 리스트"""

    return [WeekNumber(i) for i in range(1, 6)]  # 1주차부터 5주차까지
