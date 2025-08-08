from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.user.infrastructure.db_model.user import UserModel


class TagModel(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 관계 설정
    creator: Mapped["UserModel"] = relationship(
        "UserModel",
        passive_deletes=True,
    )

    # 인덱스 설정
    __table_args__ = (
        Index("idx_tag_name", "name"),
        Index("idx_tag_usage_count", "usage_count"),
        Index("idx_tag_created_by", "created_by"),
        Index("idx_tag_created_at", "created_at"),
    )
