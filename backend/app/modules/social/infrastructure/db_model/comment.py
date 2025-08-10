from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.curriculum.infrastructure.db_model.curriculum import (
        CurriculumModel,
    )
    from app.modules.user.infrastructure.db_model.user import UserModel


class CommentModel(Base):
    __tablename__: str = "comments"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    curriculum_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 인덱스 설정
    __table_args__ = (
        Index("idx_comment_curriculum", "curriculum_id"),
        Index("idx_comment_user", "user_id"),
        Index("idx_comment_created_at", "created_at"),
        Index("idx_comment_updated_at", "updated_at"),
    )

    # 관계 설정
    curriculum: Mapped["CurriculumModel"] = relationship(
        "CurriculumModel",
        passive_deletes=True,
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        passive_deletes=True,
    )
