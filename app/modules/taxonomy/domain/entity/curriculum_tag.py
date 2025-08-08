from dataclasses import dataclass
from datetime import datetime


@dataclass
class CurriculumTag:
    """커리큘럼과 태그 연결 Entity"""

    id: str
    curriculum_id: str
    tag_id: str
    added_by: str  # 태그를 추가한 사용자 ID
    created_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.curriculum_id, str) or not self.curriculum_id.strip():
            raise TypeError("curriculum_id must be a non-empty string")
        if not isinstance(self.tag_id, str) or not self.tag_id.strip():
            raise TypeError("tag_id must be a non-empty string")
        if not isinstance(self.added_by, str) or not self.added_by.strip():
            raise TypeError("added_by must be a non-empty string")
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )

    def is_added_by(self, user_id: str) -> bool:
        """특정 사용자가 추가한 태그인지 확인"""
        return self.added_by == user_id

    def __str__(self) -> str:
        return f"CurriculumTag(curriculum={self.curriculum_id}, tag={self.tag_id})"

    def __repr__(self) -> str:
        return (
            f"<CurriculumTag id={self.id} curriculum_id={self.curriculum_id} "
            f"tag_id={self.tag_id}>"
        )


@dataclass
class CurriculumCategory:
    """커리큘럼과 카테고리 연결 Entity"""

    id: str
    curriculum_id: str
    category_id: str
    assigned_by: str  # 카테고리를 할당한 사용자 ID
    created_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.curriculum_id, str) or not self.curriculum_id.strip():
            raise TypeError("curriculum_id must be a non-empty string")
        if not isinstance(self.category_id, str) or not self.category_id.strip():
            raise TypeError("category_id must be a non-empty string")
        if not isinstance(self.assigned_by, str) or not self.assigned_by.strip():
            raise TypeError("assigned_by must be a non-empty string")
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )

    def is_assigned_by(self, user_id: str) -> bool:
        """특정 사용자가 할당한 카테고리인지 확인"""
        return self.assigned_by == user_id

    def __str__(self) -> str:
        return f"CurriculumCategory(curriculum={self.curriculum_id}, category={self.category_id})"

    def __repr__(self) -> str:
        return (
            f"<CurriculumCategory id={self.id} curriculum_id={self.curriculum_id} "
            f"category_id={self.category_id}>"
        )
