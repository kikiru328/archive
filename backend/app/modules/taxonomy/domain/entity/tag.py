from dataclasses import dataclass
from datetime import datetime, timezone

from app.modules.taxonomy.domain.vo.tag_name import TagName


@dataclass
class Tag:
    """태그 Entity"""

    id: str
    name: TagName
    usage_count: int
    created_by: str  # 태그를 처음 생성한 사용자 ID
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.name, TagName):
            raise TypeError(f"name must be TagName, got {type(self.name).__name__}")
        if not isinstance(self.usage_count, int) or self.usage_count < 0:
            raise TypeError("usage_count must be a non-negative integer")
        if not isinstance(self.created_by, str) or not self.created_by.strip():
            raise TypeError("created_by must be a non-empty string")
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

    def increment_usage(self) -> None:
        """태그 사용 횟수 증가"""
        self.usage_count += 1
        self._touch_updated_at()

    def decrement_usage(self) -> None:
        """태그 사용 횟수 감소"""
        if self.usage_count > 0:
            self.usage_count -= 1
            self._touch_updated_at()

    def change_name(self, new_name: TagName) -> None:
        """태그 이름 변경"""
        if self.name != new_name:
            self.name = new_name
            self._touch_updated_at()

    def is_popular(self, threshold: int = 10) -> bool:
        """인기 태그인지 확인"""
        return self.usage_count >= threshold

    def is_created_by(self, user_id: str) -> bool:
        """특정 사용자가 생성한 태그인지 확인"""
        return self.created_by == user_id

    def can_be_deleted(self) -> bool:
        """삭제 가능 여부 확인 (사용되지 않는 태그만 삭제 가능)"""
        return self.usage_count == 0

    def __str__(self) -> str:
        return f"Tag({self.name.value})"

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name='{self.name.value}' usage={self.usage_count}>"
