from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.learning.infrastructure.db_model.summary import SummaryModel


class FeedbackModel(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    summary_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("summaries.id", ondelete="CASCADE"), nullable=False
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # 역방향 관계
    summary: Mapped["SummaryModel"] = relationship(
        "SummaryModel",
        back_populates="feedbacks",
        passive_deletes=True,
    )
