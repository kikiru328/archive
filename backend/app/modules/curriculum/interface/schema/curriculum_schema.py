from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.modules.curriculum.application.dto.curriculum_dto import (
    CreateCurriculumCommand,
    UpdateCurriculumCommand,
    CurriculumPageDTO,
    CreateWeekScheduleCommand,
    CreateLessonCommand,
    UpdateLessonCommand,
    GenerateCurriculumCommand,
)
from app.modules.curriculum.domain.vo.difficulty import Difficulty
from app.modules.curriculum.domain.vo.visibility import Visibility as VisibilityEnum


class WeekScheduleRequest(BaseModel):
    week_number: int = Field(ge=1, description="주차 번호")
    title: Optional[str] = Field(
        None, min_length=2, max_length=50, description="주차 제목(없으면 'Week {n}')"
    )
    lessons: List[str] = Field(min_length=1, description="해당 주차 수업 목록")  # type: ignoree


class CreateCurriculumRequest(BaseModel):
    title: str = Field(min_length=2, max_length=50, description="커리큘럼 제목")
    week_schedules: List[WeekScheduleRequest] = Field(  # type: ignore
        min_length=1, description="주차별 스케줄"
    )
    visibility: VisibilityEnum = Field(VisibilityEnum.PRIVATE, description="공개 여부")

    def to_dto(self, owner_id: str) -> CreateCurriculumCommand:
        # title이 있으면 (week, title, lessons), 없으면 (week, lessons)
        schedules = []
        for ws in self.week_schedules:
            if ws.title:
                schedules.append((ws.week_number, ws.title, ws.lessons))
            else:
                schedules.append((ws.week_number, ws.lessons))
        return CreateCurriculumCommand(
            owner_id=owner_id,
            title=self.title,
            week_schedules=schedules,
            visibility=self.visibility,
        )


class UpdateCurriculumRequest(BaseModel):
    title: Optional[str] = Field(
        None, min_length=2, max_length=50, description="커리큘럼 제목"
    )
    visibility: Optional[VisibilityEnum] = Field(None, description="공개 여부")

    def to_dto(self, curriculum_id: str, owner_id: str) -> UpdateCurriculumCommand:
        return UpdateCurriculumCommand(
            curriculum_id=curriculum_id,
            owner_id=owner_id,
            title=self.title,
            visibility=self.visibility,
        )


class CreateWeekScheduleRequest(BaseModel):
    week_number: int = Field(ge=1, description="추가할 주차 번호")
    lessons: List[str] = Field(min_length=1, description="해당 주차 레슨 목록")  # type: ignore
    title: Optional[str] = Field(
        None, min_length=2, max_length=50, description="주차 제목"
    )
    lessons: List[str] = Field(min_length=1, description="해당 주차 레슨 목록")  # type: ignore

    def to_dto(self, curriculum_id: str, owner_id: str) -> CreateWeekScheduleCommand:
        return CreateWeekScheduleCommand(
            curriculum_id=curriculum_id,
            owner_id=owner_id,
            week_number=self.week_number,
            lessons=self.lessons,
            title=self.title,
        )


class CreateLessonRequest(BaseModel):
    lesson: str = Field(description="추가할 레슨 내용")
    lesson_index: Optional[int] = Field(
        None, ge=0, description="삽입할 인덱스, 기본은 마지막"
    )

    def to_dto(
        self, curriculum_id: str, owner_id: str, week_number: int
    ) -> CreateLessonCommand:
        return CreateLessonCommand(
            curriculum_id=curriculum_id,
            owner_id=owner_id,
            week_number=week_number,
            lesson=self.lesson,
            lesson_index=self.lesson_index,
        )


class UpdateLessonRequest(BaseModel):
    lesson: str = Field(description="수정할 레슨 내용")

    def to_dto(
        self, curriculum_id: str, owner_id: str, week_number: int, lesson_index: int
    ) -> UpdateLessonCommand:
        return UpdateLessonCommand(
            curriculum_id=curriculum_id,
            owner_id=owner_id,
            week_number=week_number,
            lesson_index=lesson_index,
            new_lesson=self.lesson,
        )


class GenerateCurriculumRequest(BaseModel):
    goal: str = Field(description="생성 목표(예: AI 학습)")
    period: int = Field(ge=1, le=24, description="기간(주 단위)")
    difficulty: Difficulty = Field(description="난이도")
    details: Optional[str] = Field("", description="추가 세부사항")

    def to_dto(self, owner_id: str) -> GenerateCurriculumCommand:
        return GenerateCurriculumCommand(
            owner_id=owner_id,
            goal=self.goal,
            period=self.period,
            difficulty=self.difficulty,
            details=self.details or "",
        )


class CurriculumResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    visibility: VisibilityEnum
    week_schedules: List[WeekScheduleRequest]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto) -> "CurriculumResponse":
        weeks: List[WeekScheduleRequest] = [
            WeekScheduleRequest(
                week_number=week_schedule.week_number,
                title=week_schedule.title,  # ✅ 응답에 title 포함
                lessons=week_schedule.lessons,
            )
            for week_schedule in dto.week_schedules
        ]
        return cls(
            id=dto.id,
            owner_id=dto.owner_id,
            title=dto.title,
            visibility=dto.visibility,
            week_schedules=weeks,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class WeekScheduleResponse(BaseModel):
    week_number: int
    title: str
    lessons: List[str]


class CurriculumBriefResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    visibility: VisibilityEnum
    week_schedules: List[WeekScheduleResponse]
    total_weeks: int
    total_lessons: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto) -> "CurriculumBriefResponse":
        return cls(
            id=dto.id,
            owner_id=dto.owner_id,
            title=dto.title,
            visibility=dto.visibility,
            week_schedules=[  # ✅ DTO → 응답 매핑
                WeekScheduleResponse(
                    week_number=ws.week_number,
                    title=ws.title,
                    lessons=ws.lessons,
                )
                for ws in dto.week_schedules
            ],
            total_weeks=dto.total_weeks,
            total_lessons=dto.total_lessons,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class CurriculumsPageResponse(BaseModel):
    total_count: int
    page: int
    items_per_page: int
    curriculums: List[CurriculumBriefResponse]

    @classmethod
    def from_dto(cls, page_dto: CurriculumPageDTO) -> "CurriculumsPageResponse":
        items: List[CurriculumBriefResponse] = [
            CurriculumBriefResponse.from_dto(c) for c in page_dto.curriculums
        ]
        return cls(
            total_count=page_dto.total_count,
            page=page_dto.page,
            items_per_page=page_dto.items_per_page,
            curriculums=items,
        )
