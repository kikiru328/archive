from sqlalchemy import Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from app.common.db.database import Base

if TYPE_CHECKING:
    from app.modules.curriculum.infrastructure.db_model.curriculum import (
        CurriculumModel,
    )


class WeekScheduleModel(Base):
    __tablename__ = "week_schedules"

    # PK: 자동증가 정수
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # FK: curriculums.id, Curriculum 삭제 시 연쇄 삭제
    curriculum_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("curriculums.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 주차 번호(1~24)
    week_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    # 세부 커리큘럼 항목: Lessons VO의 리스트를 JSON으로 저장
    lessons: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    # 역방향 관계 설정 (DB 레벨 CASCADE 신뢰)
    curriculum: Mapped["CurriculumModel"] = relationship(
        "CurriculumModel",
        back_populates="week_schedules",
        passive_deletes=True,
    )
