from datetime import datetime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String
from app.common.db.database import Base
from app.modules.user.domain.vo.role import RoleVO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.curriculum.infrastructure.db_model.curriculum import (
        CurriculumModel,
    )
    from app.modules.social.infrastructure.db_model.like import LikeModel
    from app.modules.social.infrastructure.db_model.comment import CommentModel
    from app.modules.social.infrastructure.db_model.bookmark import BookmarkModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    email: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[RoleVO] = mapped_column(
        SQLEnum(RoleVO, name="user_role"), default=RoleVO.USER, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    curricula: Mapped[list["CurriculumModel"]] = relationship(
        "CurriculumModel",
        back_populates="user",
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
