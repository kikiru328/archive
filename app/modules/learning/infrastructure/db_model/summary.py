from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.curriculum.infrastructure.db_model.curriculum import (
        CurriculumModel,
    )
    from app.modules.learning.infrastructure.db_model.feedback import FeedbackModel


class SummaryModel(Base):
    __tablename__: str = "summaries"
    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    curriculum_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[str] = mapped_column(String(26), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 역방향 관계
    curriculum: Mapped["CurriculumModel"] = relationship(
        "CurriculumModel",
        back_populates="summaries",
        passive_deletes=True,
    )
    feedbacks: Mapped[list["FeedbackModel"]] = relationship(
        "FeedbackModel",
        back_populates="summary",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
