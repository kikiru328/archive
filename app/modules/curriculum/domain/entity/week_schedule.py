from dataclasses import dataclass

from app.modules.curriculum.domain.vo.week_number import WeekNumber
from app.modules.curriculum.domain.vo.lessons import Lessons


@dataclass
class WeekSchedule:

    week_number: WeekNumber
    lessons: Lessons

    def __post_init__(self):
        """생성 후 유효성 검사"""
        if not isinstance(self.week_number, WeekNumber):  # type: ignore
            raise TypeError(
                f"week_number must be WeekNumber, got {type(self.week_number).__name__}"
            )
        if not isinstance(self.lessons, Lessons):  # type: ignore
            raise TypeError(
                f"lessons must be Lessons, got {type(self.lessons).__name__}"
            )

    def add_lesson(self, lesson: str) -> "WeekSchedule":
        """새 레슨 추가 (불변성 유지)"""
        new_lessons = self.lessons.add_lesson(lesson)
        return WeekSchedule(week_number=self.week_number, lessons=new_lessons)

    def remove_lesson_at(self, index: int) -> "WeekSchedule":
        """지정 인덱스의 레슨 제거 (불변성 유지)"""
        new_lessons = self.lessons.remove_lesson_at(index)
        return WeekSchedule(week_number=self.week_number, lessons=new_lessons)

    def update_lesson_at(self, index: int, new_lesson: str) -> "WeekSchedule":
        """지정 인덱스의 레슨 수정 (불변성 유지)"""
        new_lessons = self.lessons.update_lesson_at(index, new_lesson)
        return WeekSchedule(week_number=self.week_number, lessons=new_lessons)

    def get_lesson_count(self) -> int:
        """레슨 개수 반환"""
        return self.lessons.count

    def has_lesson(self, lesson: str) -> bool:
        """특정 레슨 포함 여부 확인"""
        return lesson in self.lessons.items

    def __str__(self) -> str:
        return f"Week {self.week_number.value}: {len(self.lessons)} lessons"

    def __repr__(self) -> str:
        return f"<WeekSchedule week={self.week_number.value} lessons_count={len(self.lessons)}>"
