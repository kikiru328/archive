from datetime import datetime, timezone
from typing import Optional

from app.modules.social.domain.entity.follow import Follow
from app.modules.social.domain.repository.follow_repo import IFollowRepository
from app.modules.user.domain.repository.user_repo import IUserRepository


class FollowDomainService:
    """Follow 도메인 서비스"""

    def __init__(
        self,
        follow_repo: IFollowRepository,
        user_repo: IUserRepository,
    ) -> None:
        self.follow_repo = follow_repo
        self.user_repo = user_repo

    async def create_follow(
        self,
        follow_id: str,
        follower_id: str,
        followee_id: str,
        created_at: Optional[datetime] = None,
    ) -> Follow:
        """팔로우 관계 생성"""
        now = created_at or datetime.now(timezone.utc)

        # 사용자 존재 확인
        follower = await self.user_repo.find_by_id(follower_id)
        if not follower:
            raise ValueError(f"Follower user {follower_id} not found")

        followee = await self.user_repo.find_by_id(followee_id)
        if not followee:
            raise ValueError(f"Followee user {followee_id} not found")

        # 이미 팔로우 관계가 있는지 확인
        existing_follow = await self.follow_repo.find_by_follower_and_followee(
            follower_id, followee_id
        )
        if existing_follow:
            raise ValueError("Already following this user")

        follow = Follow(
            id=follow_id,
            follower_id=follower_id,
            followee_id=followee_id,
            created_at=now,
        )

        return follow

    async def can_follow(self, follower_id: str, followee_id: str) -> bool:
        """팔로우 가능 여부 확인"""
        # 자기 자신은 팔로우할 수 없음
        if follower_id == followee_id:
            return False

        # 이미 팔로우 중인지 확인
        existing_follow = await self.follow_repo.exists_follow(follower_id, followee_id)
        if existing_follow:
            return False

        # 사용자들이 존재하는지 확인
        follower = await self.user_repo.find_by_id(follower_id)
        followee = await self.user_repo.find_by_id(followee_id)

        return follower is not None and followee is not None

    async def validate_unfollow(self, follower_id: str, followee_id: str) -> bool:
        """언팔로우 가능 여부 확인"""
        return await self.follow_repo.exists_follow(follower_id, followee_id)

    async def get_follow_stats(self, user_id: str) -> dict:
        """사용자의 팔로우 통계 조회"""
        followers_count = await self.follow_repo.count_followers(user_id)
        followees_count = await self.follow_repo.count_followees(user_id)

        return {
            "followers_count": followers_count,
            "followees_count": followees_count,
        }

    async def is_following(self, follower_id: str, followee_id: str) -> bool:
        """A가 B를 팔로우하고 있는지 확인"""
        return await self.follow_repo.exists_follow(follower_id, followee_id)

    async def is_mutual_follow(self, user1_id: str, user2_id: str) -> bool:
        """서로 팔로우하고 있는지 확인"""
        follow1 = await self.follow_repo.exists_follow(user1_id, user2_id)
        follow2 = await self.follow_repo.exists_follow(user2_id, user1_id)
        return follow1 and follow2
