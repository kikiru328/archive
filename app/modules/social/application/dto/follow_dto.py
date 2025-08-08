from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.modules.social.domain.entity.follow import Follow


@dataclass
class CreateFollowCommand:
    """팔로우 생성 명령"""

    follower_id: str
    followee_id: str


@dataclass
class UnfollowCommand:
    """언팔로우 명령"""

    follower_id: str
    followee_id: str


@dataclass
class FollowQuery:
    """팔로우 조회 쿼리"""

    user_id: str
    page: int = 1
    items_per_page: int = 10


@dataclass
class FollowDTO:
    """팔로우 전송 객체"""

    id: str
    follower_id: str
    followee_id: str
    created_at: datetime

    @classmethod
    def from_domain(cls, follow: Follow) -> "FollowDTO":
        return cls(
            id=follow.id,
            follower_id=follow.follower_id,
            followee_id=follow.followee_id,
            created_at=follow.created_at,
        )


@dataclass
class UserFollowInfoDTO:
    """사용자 팔로우 정보 전송 객체"""

    user_id: str
    username: str
    email: str
    followers_count: int
    followees_count: int
    is_following: bool  # 요청한 사용자가 이 사용자를 팔로우하고 있는지
    is_followed_by: bool  # 이 사용자가 요청한 사용자를 팔로우하고 있는지

    @classmethod
    def create(
        cls,
        user_id: str,
        username: str,
        email: str,
        followers_count: int,
        followees_count: int,
        is_following: bool = False,
        is_followed_by: bool = False,
    ) -> "UserFollowInfoDTO":
        return cls(
            user_id=user_id,
            username=username,
            email=email,
            followers_count=followers_count,
            followees_count=followees_count,
            is_following=is_following,
            is_followed_by=is_followed_by,
        )


@dataclass
class FollowPageDTO:
    """팔로우 목록 페이지 전송 객체"""

    total_count: int
    page: int
    items_per_page: int
    follows: List[UserFollowInfoDTO]

    @classmethod
    def from_domain(
        cls,
        total_count: int,
        page: int,
        items_per_page: int,
        follows: List[UserFollowInfoDTO],
    ) -> "FollowPageDTO":
        return cls(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            follows=follows,
        )


@dataclass
class FollowStatsDTO:
    """팔로우 통계 전송 객체"""

    user_id: str
    followers_count: int
    followees_count: int
    mutual_followers_count: Optional[int] = None

    @classmethod
    def from_stats(cls, user_id: str, stats: dict) -> "FollowStatsDTO":
        return cls(
            user_id=user_id,
            followers_count=stats["followers_count"],
            followees_count=stats["followees_count"],
        )


@dataclass
class FollowSuggestionsDTO:
    """팔로우 추천 전송 객체"""

    suggestions: List[UserFollowInfoDTO]

    @classmethod
    def from_users(cls, users: List[UserFollowInfoDTO]) -> "FollowSuggestionsDTO":
        return cls(suggestions=users)
