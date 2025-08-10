from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Sequence, Tuple, TypeAlias

from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.vo.difficulty import Difficulty
from app.modules.curriculum.domain.vo.visibility import Visibility


WeekData: TypeAlias = Tuple[int, List[str]] | Tuple[int, Optional[str], List[str]]


@dataclass
class CreateCurriculumCommand:
    """커리큘럼 생성 명령"""

    owner_id: str
    title: str
    week_schedules: Sequence[WeekData]
    visibility: Visibility = Visibility.PRIVATE


@dataclass
class GenerateCurriculumCommand:
    """AI 커리큘럼 생성 명령"""

    owner_id: str
    goal: str
    period: int
    difficulty: Difficulty
    details: str

    def __post_init__(self):
        """유효성 검증"""
        if not self.goal.strip():
            raise ValueError("Goal cannot be empty")
        if not (1 <= self.period <= 24):
            raise ValueError("Period weeks must be between 1 and 24")
        try:
            # 이미 Difficulty 타입이면 그대로, 문자열이면 enum으로 변환
            if not isinstance(self.difficulty, Difficulty):
                self.difficulty = Difficulty(self.difficulty)  # ValueError 가능
        except ValueError:
            raise ValueError(
                "Difficulty must be one of: "
                + f"{', '.join([d.value for d in Difficulty])}"
            )


@dataclass
class UpdateCurriculumCommand:
    """커리큘럼 수정 명령"""

    curriculum_id: str
    owner_id: str
    title: Optional[str] = None
    visibility: Optional[Visibility] = None


@dataclass
class CreateWeekScheduleCommand:
    """주차 생성 명령"""

    curriculum_id: str
    owner_id: str
    week_number: int
    lessons: List[str]
    title: Optional[str] = None


@dataclass
class CreateLessonCommand:
    """레슨 생성 명령"""

    curriculum_id: str
    owner_id: str
    week_number: int
    lesson: str
    lesson_index: Optional[int] = None


@dataclass
class UpdateLessonCommand:
    """레슨 수정 명령"""

    curriculum_id: str
    owner_id: str
    week_number: int
    lesson_index: int
    new_lesson: str


@dataclass
class DeleteLessonCommand:
    """레슨 삭제 명령"""

    curriculum_id: str
    owner_id: str
    week_number: int
    lesson_index: int


@dataclass
class CurriculumQuery:
    """커리큘럼 조회 쿼리"""

    owner_id: Optional[str] = None
    page: int = 1
    items_per_page: int = 10
    visibility: Optional[Visibility] = None


@dataclass
class WeekScheduleDTO:
    """주차 스케줄 전송 객체"""

    week_number: int
    title: str
    lessons: List[str]

    @classmethod
    def from_domain(cls, week_schedule: WeekSchedule) -> "WeekScheduleDTO":
        return cls(
            week_number=week_schedule.week_number.value,
            title=week_schedule.title.value,
            lessons=week_schedule.lessons.items,
        )


@dataclass
class CurriculumDTO:
    """커리큘럼 전송 객체"""

    id: str
    owner_id: str
    title: str
    visibility: str
    created_at: datetime
    updated_at: datetime
    week_schedules: List[WeekScheduleDTO]

    @classmethod
    def from_domain(cls, curriculum: Curriculum) -> "CurriculumDTO":
        return cls(
            id=curriculum.id,
            owner_id=curriculum.owner_id,
            title=curriculum.title.value,
            visibility=curriculum.visibility.value,
            created_at=curriculum.created_at,
            updated_at=curriculum.updated_at,
            week_schedules=[
                WeekScheduleDTO.from_domain(ws) for ws in curriculum.week_schedules
            ],
        )


@dataclass
class CurriculumBriefDTO:
    """커리큘럼 요약 전송 객체"""

    id: str
    owner_id: str
    title: str
    visibility: str
    week_schedules: List[WeekScheduleDTO]
    total_weeks: int
    total_lessons: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, curriculum: Curriculum) -> "CurriculumBriefDTO":
        return cls(
            id=curriculum.id,
            owner_id=curriculum.owner_id,
            title=curriculum.title.value,
            visibility=curriculum.visibility.value,
            week_schedules=[  # ✅ 도메인 → DTO 매핑
                WeekScheduleDTO.from_domain(ws) for ws in curriculum.week_schedules
            ],
            total_weeks=curriculum.get_total_weeks(),
            total_lessons=curriculum.get_total_lessons(),
            created_at=curriculum.created_at,
            updated_at=curriculum.updated_at,
        )


@dataclass
class CurriculumPageDTO:
    """커리큘럼 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    curriculums: List[CurriculumBriefDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        curriculums: List[Curriculum],
    ) -> "CurriculumPageDTO":
        curriculum_dtos: List[CurriculumBriefDTO] = [
            CurriculumBriefDTO.from_domain(c) for c in curriculums
        ]
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            curriculums=curriculum_dtos,
        )
