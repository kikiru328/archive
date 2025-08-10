from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.user.infrastructure.db_model.user import UserModel


class FollowModel(Base):
    __tablename__ = "follows"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    follower_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    followee_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 제약 조건: 같은 팔로우 관계 중복 방지
    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="unique_follow_relation"),
        Index("idx_follow_follower", "follower_id"),
        Index("idx_follow_followee", "followee_id"),
        Index("idx_follow_created_at", "created_at"),
        # 팔로워/팔로위 조회 성능 최적화
        Index("idx_follow_follower_created", "follower_id", "created_at"),
        Index("idx_follow_followee_created", "followee_id", "created_at"),
    )

    # 관계 설정
    follower: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[follower_id],
        passive_deletes=True,
    )
    followee: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[followee_id],
        passive_deletes=True,
    )
