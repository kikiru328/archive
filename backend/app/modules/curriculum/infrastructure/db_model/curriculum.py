from datetime import datetime
from app.common.db.database import Base
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.modules.user.infrastructure.db_model.user import UserModel
    from app.modules.curriculum.infrastructure.db_model.week_schedule import (
        WeekScheduleModel,
    )
    from app.modules.learning.infrastructure.db_model.summary import SummaryModel
    from app.modules.social.infrastructure.db_model.like import LikeModel
    from app.modules.social.infrastructure.db_model.comment import CommentModel
    from app.modules.social.infrastructure.db_model.bookmark import BookmarkModel


class CurriculumModel(Base):
    __tablename__ = "curriculums"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    visibility: Mapped[str] = mapped_column(
        String(10), nullable=False, default="PRIVATE"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # relationship
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="curricula",
        passive_deletes=True,
    )

    week_schedules: Mapped[list["WeekScheduleModel"]] = relationship(
        "WeekScheduleModel",
        back_populates="curriculum",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    summaries: Mapped[list["SummaryModel"]] = relationship(
        "SummaryModel",
        back_populates="curriculum",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    likes: Mapped[list["LikeModel"]] = relationship(
        "LikeModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    comments: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    bookmarks: Mapped[list["BookmarkModel"]] = relationship(
        "BookmarkModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
