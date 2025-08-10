from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.curriculum.infrastructure.db_model.curriculum import (
        CurriculumModel,
    )
    from app.modules.user.infrastructure.db_model.user import UserModel


class LikeModel(Base):
    __tablename__ = "likes"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    curriculum_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 중복 방지: 같은 사용자가 같은 커리큘럼에 중복 좋아요 방지
    __table_args__ = (
        UniqueConstraint("curriculum_id", "user_id", name="unique_curriculum_like"),
        Index("idx_like_curriculum", "curriculum_id"),
        Index("idx_like_user", "user_id"),
        Index("idx_like_created_at", "created_at"),
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
