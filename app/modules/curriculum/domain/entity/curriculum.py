from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from app.modules.curriculum.domain.vo import Title, Visibility, WeekNumber
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule


@dataclass
class Curriculum:
    """커리큘럼 핵심 Entity"""

    id: str
    owner_id: str
    title: Title
    visibility: Visibility
    created_at: datetime
    updated_at: datetime
    week_schedules: List[WeekSchedule] = field(default_factory=list)  # type: ignore

    def __post_init__(self):
        """생성 후 유효성 검사"""
        if not isinstance(self.id, str) or not self.id.strip():  # type: ignore
            raise ValueError("id must be a non-empty string")

        if not isinstance(self.owner_id, str) or not self.owner_id.strip():  # type: ignore
            raise ValueError("owner_id must be a non-empty string")

        if not isinstance(self.title, Title):  # type: ignore
            raise TypeError(f"title must be Title, got {type(self.title).__name__}")

        if not isinstance(self.visibility, Visibility):  # type: ignore
            raise TypeError(
                f"visibility must be Visibility, got {type(self.visibility).__name__}"
            )
        if not isinstance(self.created_at, datetime):  # type: ignore
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )
        if not isinstance(self.updated_at, datetime):  # type: ignore
            raise TypeError(
                f"updated_at must be datetime, got {type(self.updated_at).__name__}"
            )
        if not isinstance(self.week_schedules, list):  # type: ignore
            raise TypeError("week_schedules must be a list")

        if not all(isinstance(week_schedule, WeekSchedule) for week_schedule in self.week_schedules):  # type: ignore
            raise TypeError("All items in week_topics must be WeekTopic instances")

        # 주차 번호 중복 검사
        week_numbers = [
            week_schedule.week_number.value for week_schedule in self.week_schedules
        ]
        if len(week_numbers) != len(set(week_numbers)):
            raise ValueError("Duplicate week numbers are not allowed")

        # 주차 번호 정렬
        self.week_schedules.sort(
            key=lambda week_schedule: week_schedule.week_number.value
        )

    def _touch_updated_at(self) -> None:
        """updated_at 갱신"""
        self.updated_at = datetime.now(timezone.utc)

    def add_week_schedule(self, week_schedule: WeekSchedule) -> None:
        """주차별 주제 추가 (비즈니스 로직)"""
        # 중복 주차 검사
        existing_weeks = [
            week_schedule.week_number for week_schedule in self.week_schedules
        ]
        if week_schedule.week_number in existing_weeks:
            raise ValueError(f"Week {week_schedule.week_number.value} already exists")

        # 최대 주차 제한 (24주)
        if week_schedule.week_number.value > WeekNumber.MAX_WEEK:
            raise ValueError(f"Cannot add more than {WeekNumber.MAX_WEEK} weeks")

        if len(self.week_schedules) >= WeekNumber.MAX_WEEK:
            raise ValueError(f"Cannot add more than {WeekNumber.MAX_WEEK} weeks")

        self.week_schedules.append(week_schedule)
        self.week_schedules.sort(
            key=lambda week_schedule: week_schedule.week_number.value
        )
        self._touch_updated_at()

    def remove_week_schedule(self, week_number: WeekNumber) -> None:
        """주차별 주제 제거"""
        initial_count = len(self.week_schedules)
        self.week_schedules = [
            week_schedule
            for week_schedule in self.week_schedules
            if week_schedule.week_number != week_number
        ]

        if len(self.week_schedules) == initial_count:
            raise ValueError(f"Week {week_number.value} not found")

        self._touch_updated_at()

    def get_week_schedule(self, week_number: WeekNumber) -> Optional[WeekSchedule]:
        """특정 주차 주제 조회"""
        print(f"Looking for week: {week_number.value}")
        print(
            f"Available weeks: {[ws.week_number.value for ws in self.week_schedules]}"
        )
        for week_schedule in self.week_schedules:
            if week_schedule.week_number == week_number:
                return week_schedule
        return None

    def update_week_schedule(
        self,
        week_number: WeekNumber,
        new_week_schedule: WeekSchedule,
    ) -> None:
        """특정 주차 주제 수정"""
        if new_week_schedule.week_number != week_number:
            raise ValueError("Week number mismatch")

        for i, week_schedule in enumerate(self.week_schedules):
            if week_schedule.week_number == week_number:
                self.week_schedules[i] = new_week_schedule
                self._touch_updated_at()
                return

        raise ValueError(f"Week {week_number.value} not found")

    def change_title(self, new_title: Title) -> None:
        """제목 변경"""
        if self.title == new_title:
            return

        self.title = new_title
        self._touch_updated_at()

    def change_visibility(self, new_visibility: Visibility) -> None:
        """공개 설정 변경"""
        if self.visibility == new_visibility:
            return

        self.visibility = new_visibility
        self._touch_updated_at()

    def make_public(self) -> None:
        """공개로 변경"""
        self.change_visibility(Visibility.PUBLIC)

    def make_private(self) -> None:
        """비공개로 변경"""
        self.change_visibility(Visibility.PRIVATE)

    def is_public(self) -> bool:
        """공개 여부 확인"""
        return self.visibility.is_public()

    def is_private(self) -> bool:
        """비공개 여부 확인"""
        return self.visibility.is_private()

    def is_owned_by(self, user_id: str) -> bool:
        """소유자 확인"""
        return self.owner_id == user_id

    def get_total_weeks(self) -> int:
        """전체 주차 수"""
        return len(self.week_schedules)

    def get_total_lessons(self) -> int:
        """전체 레슨 수"""
        return sum(
            week_schedule.get_lesson_count() for week_schedule in self.week_schedules
        )

    def get_week_numbers(self) -> List[int]:
        """주차 번호 목록"""
        return [
            week_schedule.week_number.value for week_schedule in self.week_schedules
        ]

    def has_week(self, week_number: WeekNumber) -> bool:
        """특정 주차 존재 여부"""
        return any(
            week_schedule.week_number == week_number
            for week_schedule in self.week_schedules
        )

    def is_empty(self) -> bool:
        """빈 커리큘럼인지 확인"""
        return len(self.week_schedules) == 0

    def __str__(self) -> str:
        return f"{self.title.value} ({self.get_total_weeks()} weeks)"

    def __repr__(self) -> str:
        return (
            f"<Curriculum id={self.id} title='{self.title.value}' "
            f"weeks={self.get_total_weeks()} visibility={self.visibility.value}>"
        )
