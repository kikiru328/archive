from datetime import datetime, timezone
from typing import List, Optional, Sequence, Tuple, TypeAlias

from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.curriculum.domain.vo import Title, Visibility, Lessons, WeekNumber

WeekData: TypeAlias = Tuple[int, List[str]] | Tuple[int, Optional[str], List[str]]


class CurriculumDomainService:

    def __init__(self, curriculum_repo: ICurriculumRepository) -> None:
        self.curriculum_repo: ICurriculumRepository = curriculum_repo

    # 기본 제목 생성
    def _default_title(
        self, n: int, lessons: list[str] | None = None, goal: str | None = None
    ) -> str:
        # 접두사 없이 "핵심 요약"만 — 우선 첫 레슨, 없으면 goal 일부
        if lessons and len(lessons) > 0:
            return str(lessons[0])[:50]
        return (goal or f"Week {n}")[:50]

    # 기본 제목일 때만 자동 리네이밍
    def _shift_title_if_default(self, title: str, old_n: int, new_n: int) -> str:
        return title

    async def create_curriculum(
        self,
        curriculum_id: str,
        owner_id: str,
        title: str,
        week_schedules_data: Sequence[WeekData],
        visibility: Visibility = Visibility.PRIVATE,
        created_at: Optional[datetime] = None,
    ) -> Curriculum:

        now = created_at or datetime.now(timezone.utc)

        week_schedules: list[WeekSchedule] = []
        for item in week_schedules_data:
            # (week_num, lessons) 또는 (week_num, title|None, lessons)
            if len(item) == 2:
                week_num, lessons_data = item  # type: ignore[misc]
                title_raw = self._default_title(week_num, lessons=list(lessons_data))
            else:
                week_num, title_opt, lessons_data = item  # type: ignore[misc]
                title_raw = title_opt or self._default_title(
                    week_num, lessons=list(lessons_data)
                )

            week_number = WeekNumber(int(week_num))
            lessons = Lessons(list(lessons_data))
            week_schedule = WeekSchedule(
                week_number=week_number,
                title=Title(title_raw),
                lessons=lessons,
            )
            week_schedules.append(week_schedule)

        return Curriculum(
            id=curriculum_id,
            owner_id=owner_id,
            title=Title(title),
            visibility=visibility,
            created_at=now,
            updated_at=now,
            week_schedules=week_schedules,
        )

    async def insert_week_and_shift(
        self,
        curriculum: Curriculum,
        new_week_number: int,
        lessons_data: List[str],
        new_week_title: Optional[str] = None,
    ) -> Curriculum:
        """새 주차 삽입 및 기존 주차들 뒤로 밀기"""
        new_week = WeekNumber(new_week_number)
        new_lessons = Lessons(lessons_data)
        # 새 주차 제목: 주어지지 않으면 기본 제목
        new_title = Title(
            new_week_title or self._default_title(new_week_number, lessons=lessons_data)
        )
        new_week_schedule = WeekSchedule(
            week_number=new_week, title=new_title, lessons=new_lessons
        )

        # 새 주차 이후의 모든 주차를 1씩 증가
        updated_week_schedules: list[WeekSchedule] = []
        inserted = False

        for week_schedule in curriculum.week_schedules:
            if week_schedule.week_number.value >= new_week_number and not inserted:
                # 새 주차 삽입
                updated_week_schedules.append(new_week_schedule)
                inserted = True

                # 기존 주차는 번호를 1 증가시켜 추가
                if week_schedule.week_number.value < WeekNumber.MAX_WEEK:
                    shifted_week = WeekNumber(week_schedule.week_number.value + 1)
                    # 제목은 그대로 유지
                    shifted_title = week_schedule.title
                    shifted_week_schedule = WeekSchedule(
                        week_number=shifted_week,
                        title=shifted_title,
                        lessons=week_schedule.lessons,
                    )
                    updated_week_schedules.append(shifted_week_schedule)
            elif week_schedule.week_number.value >= new_week_number:
                # 이후 주차들 번호 증가
                if week_schedule.week_number.value < WeekNumber.MAX_WEEK:
                    shifted_week = WeekNumber(week_schedule.week_number.value + 1)
                    shifted_title = week_schedule.title
                    shifted_week_schedule = WeekSchedule(
                        week_number=shifted_week,
                        title=shifted_title,
                        lessons=week_schedule.lessons,
                    )
                    updated_week_schedules.append(shifted_week_schedule)
            else:
                # 이전 주차들은 그대로 유지
                updated_week_schedules.append(week_schedule)

        # 마지막에 추가하는 경우
        if not inserted:
            updated_week_schedules.append(new_week_schedule)

        # 새 커리큘럼 생성 (불변성 유지)
        return Curriculum(
            id=curriculum.id,
            owner_id=curriculum.owner_id,
            title=curriculum.title,
            visibility=curriculum.visibility,
            created_at=curriculum.created_at,
            updated_at=datetime.now(timezone.utc),
            week_schedules=updated_week_schedules,
        )

    async def remove_week_and_shift(
        self,
        curriculum: Curriculum,
        target_week_number: int,
    ) -> Curriculum:
        """주차 제거 및 이후 주차들 앞으로 당기기"""
        target_week = WeekNumber(target_week_number)

        # 해당 주차가 존재하는지 확인
        if not curriculum.has_week(target_week):
            raise ValueError(f"Week {target_week_number} not found")

        updated_week_schedules: list[WeekSchedule] = []

        for week_schedule in curriculum.week_schedules:
            if week_schedule.week_number == target_week:
                # 제거할 주차는 스킵
                continue
            elif week_schedule.week_number.value > target_week_number:
                # 이후 주차들은 번호를 1 감소
                shifted_week = WeekNumber(week_schedule.week_number.value - 1)
                shifted_title = week_schedule.title
                shifted_week_schedule = WeekSchedule(
                    week_number=shifted_week,
                    title=shifted_title,
                    lessons=week_schedule.lessons,
                )
                updated_week_schedules.append(shifted_week_schedule)
            else:
                # 이전 주차들은 그대로 유지
                updated_week_schedules.append(week_schedule)

        return Curriculum(
            id=curriculum.id,
            owner_id=curriculum.owner_id,
            title=curriculum.title,
            visibility=curriculum.visibility,
            created_at=curriculum.created_at,
            updated_at=datetime.now(timezone.utc),
            week_schedules=updated_week_schedules,
        )

    async def validate_curriculum_structure(
        self,
        curriculum: Curriculum,
    ) -> bool:
        """커리큘럼 구조 유효성 검증"""
        # 빈 커리큘럼 허용하지 않음
        if curriculum.is_empty():
            return False

        # 주차 번호 연속성 검증 (1부터 시작해야 함)
        week_numbers = curriculum.get_week_numbers()
        if week_numbers[0] != 1:
            return False

        # 주차 번호가 연속적인지 검증
        for i in range(1, len(week_numbers)):
            if week_numbers[i] != week_numbers[i - 1] + 1:
                return False

        return True

    async def can_access_curriculum(
        self,
        curriculum: Curriculum,
        user_id: str,
        is_admin: bool = False,
    ) -> bool:
        """커리큘럼 접근 권한 검증"""
        # 관리자는 모든 커리큘럼 접근 가능
        if is_admin:
            return True

        # 소유자는 항상 접근 가능
        if curriculum.is_owned_by(user_id):
            return True

        # 공개 커리큘럼은 누구나 접근 가능
        if curriculum.is_public():
            return True

        return False
