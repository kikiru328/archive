from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.modules.social.application.dto.follow_dto import (
    CreateFollowCommand,
    UnfollowCommand,
    FollowDTO,
    UserFollowInfoDTO,
    FollowPageDTO,
    FollowStatsDTO,
    FollowSuggestionsDTO,
)


class FollowUserRequest(BaseModel):
    """사용자 팔로우 요청"""

    followee_id: str = Field(description="팔로우할 사용자 ID")

    def to_command(self, follower_id: str) -> CreateFollowCommand:
        return CreateFollowCommand(
            follower_id=follower_id,
            followee_id=self.followee_id,
        )


class UnfollowUserRequest(BaseModel):
    """사용자 언팔로우 요청"""

    followee_id: str = Field(description="언팔로우할 사용자 ID")

    def to_command(self, follower_id: str) -> UnfollowCommand:
        return UnfollowCommand(
            follower_id=follower_id,
            followee_id=self.followee_id,
        )


class FollowResponse(BaseModel):
    """팔로우 응답"""

    id: str
    follower_id: str
    followee_id: str
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: FollowDTO) -> "FollowResponse":
        return cls(
            id=dto.id,
            follower_id=dto.follower_id,
            followee_id=dto.followee_id,
            created_at=dto.created_at,
        )


class UserFollowInfoResponse(BaseModel):
    """사용자 팔로우 정보 응답"""

    user_id: str
    username: str
    email: str
    followers_count: int
    followees_count: int
    is_following: bool
    is_followed_by: bool

    @classmethod
    def from_dto(cls, dto: UserFollowInfoDTO) -> "UserFollowInfoResponse":
        return cls(
            user_id=dto.user_id,
            username=dto.username,
            email=dto.email,
            followers_count=dto.followers_count,
            followees_count=dto.followees_count,
            is_following=dto.is_following,
            is_followed_by=dto.is_followed_by,
        )


class FollowersResponse(BaseModel):
    """팔로워 목록 응답"""

    total_count: int
    page: int
    items_per_page: int
    followers: List[UserFollowInfoResponse]

    @classmethod
    def from_dto(cls, dto: FollowPageDTO) -> "FollowersResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            followers=[UserFollowInfoResponse.from_dto(f) for f in dto.follows],
        )


class FolloweesResponse(BaseModel):
    """팔로잉 목록 응답"""

    total_count: int
    page: int
    items_per_page: int
    followees: List[UserFollowInfoResponse]

    @classmethod
    def from_dto(cls, dto: FollowPageDTO) -> "FolloweesResponse":
        return cls(
            total_count=dto.total_count,
            page=dto.page,
            items_per_page=dto.items_per_page,
            followees=[UserFollowInfoResponse.from_dto(f) for f in dto.follows],
        )


class FollowStatsResponse(BaseModel):
    """팔로우 통계 응답"""

    user_id: str
    followers_count: int
    followees_count: int
    mutual_followers_count: Optional[int] = None

    @classmethod
    def from_dto(cls, dto: FollowStatsDTO) -> "FollowStatsResponse":
        return cls(
            user_id=dto.user_id,
            followers_count=dto.followers_count,
            followees_count=dto.followees_count,
            mutual_followers_count=dto.mutual_followers_count,
        )


class FollowStatusResponse(BaseModel):
    """팔로우 상태 응답"""

    is_following: bool
    is_mutual: bool


class FollowSuggestionsResponse(BaseModel):
    """팔로우 추천 응답"""

    suggestions: List[UserFollowInfoResponse]

    @classmethod
    def from_dto(cls, dto: FollowSuggestionsDTO) -> "FollowSuggestionsResponse":
        return cls(
            suggestions=[UserFollowInfoResponse.from_dto(s) for s in dto.suggestions]
        )
