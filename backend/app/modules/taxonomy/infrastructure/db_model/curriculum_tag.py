from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.db.database import Base
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.modules.curriculum.infrastructure.db_model.curriculum import (
        CurriculumModel,
    )
    from app.modules.taxonomy.infrastructure.db_model.tag import TagModel
    from app.modules.taxonomy.infrastructure.db_model.category import CategoryModel
    from app.modules.user.infrastructure.db_model.user import UserModel


class CurriculumTagModel(Base):
    __tablename__ = "curriculum_tags"

    id: Mapped[str] = mapped_column(String(53), primary_key=True)
    curriculum_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )
    tag_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
    )
    added_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 중복 방지: 같은 커리큘럼에 같은 태그 중복 연결 방지
    __table_args__ = (
        UniqueConstraint("curriculum_id", "tag_id", name="unique_curriculum_tag"),
        Index("idx_curriculum_tag_curriculum", "curriculum_id"),
        Index("idx_curriculum_tag_tag", "tag_id"),
        Index("idx_curriculum_tag_added_by", "added_by"),
        Index("idx_curriculum_tag_created_at", "created_at"),
    )

    # 관계 설정
    curriculum: Mapped["CurriculumModel"] = relationship(
        "CurriculumModel",
        passive_deletes=True,
    )
    tag: Mapped["TagModel"] = relationship(
        "TagModel",
        passive_deletes=True,
    )
    added_by_user: Mapped["UserModel"] = relationship(
        "UserModel",
        passive_deletes=True,
    )


class CurriculumCategoryModel(Base):
    __tablename__ = "curriculum_categories"

    id: Mapped[str] = mapped_column(String(53), primary_key=True)
    curriculum_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    assigned_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 제약 조건: 한 커리큘럼은 하나의 카테고리만 가질 수 있음
    __table_args__ = (
        UniqueConstraint("curriculum_id", name="unique_curriculum_category"),
        Index("idx_curriculum_category_curriculum", "curriculum_id"),
        Index("idx_curriculum_category_category", "category_id"),
        Index("idx_curriculum_category_assigned_by", "assigned_by"),
        Index("idx_curriculum_category_created_at", "created_at"),
    )

    # 관계 설정
    curriculum: Mapped["CurriculumModel"] = relationship(
        "CurriculumModel",
        passive_deletes=True,
    )
    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel",
        passive_deletes=True,
    )
    assigned_by_user: Mapped["UserModel"] = relationship(
        "UserModel",
        passive_deletes=True,
    )
