from typing import List, Any

from app.modules.curriculum.domain.vo.lesson import Lesson


class Lessons:
    """Lessons (list)"""

    __slots__ = ("_items",)

    MIN_COUNT = 1
    MAX_COUNT = 5

    def __init__(self, raw: List[Any]) -> None:
        if not isinstance(raw, list):  # type: ignore
            raise ValueError(f"Lessons must be a list, got {type(raw).__name__}")

        # Lesson VO로 변환하면서 빈 값 제거
        lessons: List[Lesson] = []
        for i, item in enumerate(raw):
            if not isinstance(item, str):
                raise ValueError(
                    f"Lesson at index {i} must be a string, got {type(item).__name__}"
                )

            text = item.strip()
            if text:  # 빈 문자열이 아닌 경우만 추가
                lessons.append(Lesson(text))

        count = len(lessons)
        if count < self.MIN_COUNT:
            raise ValueError(f"Lessons must have at least {self.MIN_COUNT} item")
        if count > self.MAX_COUNT:
            raise ValueError(
                f"Lessons cannot exceed {self.MAX_COUNT} items (got {count})"
            )

        self._items = tuple(lessons)  # 불변성 보장

    @property
    def items(self) -> List[str]:
        """문자열 리스트로 반환"""
        return [lesson.value for lesson in self._items]

    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def lessons(self) -> List[Lesson]:
        """Lesson VO 리스트로 반환"""
        return list(self._items)

    def add_lesson(self, lesson: str) -> "Lessons":
        """새 레슨 추가한 Lessons 반환 (불변성 유지)"""
        if self.count >= self.MAX_COUNT:
            raise ValueError(f"Cannot add more than {self.MAX_COUNT} lessons")

        new_lessons = list(self._items) + [Lesson(lesson)]
        return Lessons([lesson.value for lesson in new_lessons])

    def remove_lesson_at(self, index: int) -> "Lessons":
        """지정 인덱스의 레슨 제거한 Lessons 반환 (불변성 유지)"""
        if not (0 <= index < self.count):
            raise ValueError(f"Index {index} out of range (0-{self.count-1})")

        if self.count <= self.MIN_COUNT:
            raise ValueError(f"Cannot remove lesson, minimum {self.MIN_COUNT} required")

        new_lessons = list(self._items)
        new_lessons.pop(index)
        return Lessons([lesson.value for lesson in new_lessons])

    def update_lesson_at(self, index: int, new_lesson: str) -> "Lessons":
        """지정 인덱스의 레슨 수정한 Lessons 반환 (불변성 유지)"""
        if not (0 <= index < self.count):
            raise ValueError(f"Index {index} out of range (0-{self.count-1})")

        new_lessons = list(self._items)
        new_lessons[index] = Lesson(new_lesson)
        return Lessons([lesson.value for lesson in new_lessons])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Lessons) and self._items == other._items

    def __hash__(self) -> int:
        return hash(self._items)

    def __repr__(self) -> str:
        return f"<Lessons {[lesson.value for lesson in self._items]}>"

    def __iter__(self):
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> Lesson:
        return self._items[index]
