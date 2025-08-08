from dataclasses import dataclass
from datetime import datetime


@dataclass
class Follow:
    """팔로우 관계 Entity"""

    id: str
    follower_id: str  # 팔로우하는 사람
    followee_id: str  # 팔로우당하는 사람
    created_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise TypeError("id must be a non-empty string")
        if not isinstance(self.follower_id, str) or not self.follower_id.strip():
            raise TypeError("follower_id must be a non-empty string")
        if not isinstance(self.followee_id, str) or not self.followee_id.strip():
            raise TypeError("followee_id must be a non-empty string")
        if not isinstance(self.created_at, datetime):
            raise TypeError(
                f"created_at must be datetime, got {type(self.created_at).__name__}"
            )

        # 자기 자신을 팔로우할 수 없음
        if self.follower_id == self.followee_id:
            raise ValueError("Cannot follow yourself")

    def is_follower(self, user_id: str) -> bool:
        """특정 사용자가 팔로워인지 확인"""
        return self.follower_id == user_id

    def is_followee(self, user_id: str) -> bool:
        """특정 사용자가 팔로위인지 확인"""
        return self.followee_id == user_id

    def involves_user(self, user_id: str) -> bool:
        """특정 사용자가 이 팔로우 관계에 포함되는지 확인"""
        return self.is_follower(user_id) or self.is_followee(user_id)

    def __str__(self) -> str:
        return f"Follow({self.follower_id} -> {self.followee_id})"

    def __repr__(self) -> str:
        return (
            f"<Follow id={self.id} follower={self.follower_id} "
            f"followee={self.followee_id}>"
        )
