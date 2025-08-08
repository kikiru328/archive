from dataclasses import dataclass
from datetime import datetime


@dataclass
class Bookmark:
    """북마크 Entity"""

    id: str
    curriculum_id: str
    user_id: str
    created_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.curriculum_id, str) or not self.curriculum_id.strip():
            raise TypeError("curriculum_id must be a non-empty string")
        if not isinstance(self.user_id, str) or not self.user_id.strip():
            raise TypeError("user_id must be a non-empty string")
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )

    def is_bookmarked_by(self, user_id: str) -> bool:
        """특정 사용자가 북마크한 것인지 확인"""
        return self.user_id == user_id

    def __str__(self) -> str:
        return f"Bookmark(curriculum={self.curriculum_id}, user={self.user_id})"

    def __repr__(self) -> str:
        return f"<Bookmark id={self.id} curriculum_id={self.curriculum_id} user_id={self.user_id}>"
