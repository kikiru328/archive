from dataclasses import dataclass
from datetime import datetime, timezone

from app.modules.social.domain.vo.comment_content import CommentContent


@dataclass
class Comment:
    """댓글 Entity"""

    id: str
    curriculum_id: str
    user_id: str
    content: CommentContent
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.curriculum_id, str) or not self.curriculum_id.strip():
            raise TypeError("curriculum_id must be a non-empty string")
        if not isinstance(self.user_id, str) or not self.user_id.strip():
            raise TypeError("user_id must be a non-empty string")
        if not isinstance(self.content, CommentContent):
            raise TypeError(
                f"content must be CommentContent, got {type(self.content).__name__}"
            )
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )
        if not isinstance(self.updated_at, datetime):
            raise TypeError(
                f"updated_at must be datetime, got {type(self.updated_at).__name__}"
            )

    def _touch_updated_at(self) -> None:
        """updated_at 갱신"""
        self.updated_at = datetime.now(timezone.utc)

    def update_content(self, new_content: CommentContent) -> None:
        """댓글 내용 수정"""
        if self.content == new_content:
            return

        self.content = new_content
        self._touch_updated_at()

    def is_written_by(self, user_id: str) -> bool:
        """특정 사용자가 작성한 댓글인지 확인"""
        return self.user_id == user_id

    def can_be_modified_by(self, user_id: str, is_admin: bool = False) -> bool:
        """특정 사용자가 수정할 수 있는지 확인"""
        return is_admin or self.is_written_by(user_id)

    def __str__(self) -> str:
        snippet = (
            self.content.value[:50] + "..."
            if len(self.content.value) > 50
            else self.content.value
        )
        return f"Comment: {snippet}"

    def __repr__(self) -> str:
        return f"<Comment id={self.id} curriculum_id={self.curriculum_id} user_id={self.user_id}>"
