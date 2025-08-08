from typing import List
from ulid import ULID  # type: ignore

from app.modules.social.application.dto.follow_dto import (
    CreateFollowCommand,
    UnfollowCommand,
    FollowQuery,
    FollowDTO,
    UserFollowInfoDTO,
    FollowPageDTO,
    FollowStatsDTO,
    FollowSuggestionsDTO,
)
from app.modules.social.application.exception import (
    AlreadyFollowingError,
    NotFollowingError,
    SelfFollowError,
    UserNotFoundError,
)
from app.modules.social.domain.entity.follow import Follow
from app.modules.social.domain.repository.follow_repo import IFollowRepository
from app.modules.social.domain.service.follow_domain_service import FollowDomainService
from app.modules.user.domain.repository.user_repo import IUserRepository
from app.modules.user.domain.entity.user import User


class FollowService:
    """팔로우 애플리케이션 서비스"""

    def __init__(
        self,
        follow_repo: IFollowRepository,
        user_repo: IUserRepository,
        follow_domain_service: FollowDomainService,
        ulid: ULID = ULID(),
    ) -> None:
        self.follow_repo: IFollowRepository = follow_repo
        self.user_repo: IUserRepository = user_repo
        self.follow_domain_service: FollowDomainService = follow_domain_service
        self.ulid: ULID = ulid

    async def follow_user(self, command: CreateFollowCommand) -> FollowDTO:
        """사용자 팔로우"""
        # 자기 자신 팔로우 체크
        if command.follower_id == command.followee_id:
            raise SelfFollowError("Cannot follow yourself")

        # 팔로우 가능 여부 확인
        can_follow: bool = await self.follow_domain_service.can_follow(
            command.follower_id, command.followee_id
        )
        if not can_follow:
            # 더 구체적인 에러 확인
            follower: User | None = await self.user_repo.find_by_id(command.follower_id)
            followee: User | None = await self.user_repo.find_by_id(command.followee_id)

            if not follower or not followee:
                raise UserNotFoundError("User not found")

            already_following: bool = await self.follow_repo.exists_follow(
                command.follower_id, command.followee_id
            )
            if already_following:
                raise AlreadyFollowingError("Already following this user")

        try:
            follow: Follow = await self.follow_domain_service.create_follow(
                follow_id=self.ulid.generate(),
                follower_id=command.follower_id,
                followee_id=command.followee_id,
            )

            await self.follow_repo.save(follow)
            return FollowDTO.from_domain(follow)

        except ValueError as e:
            if "Already following" in str(e):
                raise AlreadyFollowingError(str(e))
            elif "not found" in str(e):
                raise UserNotFoundError(str(e))
            raise

    async def unfollow_user(self, command: UnfollowCommand) -> None:
        """사용자 언팔로우"""
        # 팔로우 관계 존재 확인
        is_following: bool = await self.follow_domain_service.validate_unfollow(
            command.follower_id, command.followee_id
        )
        if not is_following:
            raise NotFollowingError("Not following this user")

        await self.follow_repo.delete_by_follower_and_followee(
            command.follower_id, command.followee_id
        )

    async def get_followers(
        self, query: FollowQuery, requester_id: str
    ) -> FollowPageDTO:
        """팔로워 목록 조회"""
        total_count, follows = await self.follow_repo.find_followers(
            query.user_id, query.page, query.items_per_page
        )

        user_infos = []
        for follow in follows:
            follower: User | None = await self.user_repo.find_by_id(follow.follower_id)
            if not follower:
                continue

            # 요청자와의 팔로우 관계 확인
            is_following: bool = await self.follow_domain_service.is_following(
                requester_id, follower.id
            )
            is_followed_by: bool = await self.follow_domain_service.is_following(
                follower.id, requester_id
            )

            # 팔로우 통계
            stats = await self.follow_domain_service.get_follow_stats(follower.id)

            user_info = UserFollowInfoDTO.create(
                user_id=follower.id,
                username=follower.name.value,
                email=follower.email.value,
                followers_count=stats["followers_count"],
                followees_count=stats["followees_count"],
                is_following=is_following,
                is_followed_by=is_followed_by,
            )
            user_infos.append(user_info)

        return FollowPageDTO.from_domain(
            total_count, query.page, query.items_per_page, user_infos
        )

    async def get_followees(
        self, query: FollowQuery, requester_id: str
    ) -> FollowPageDTO:
        """팔로잉 목록 조회"""
        total_count, follows = await self.follow_repo.find_followees(
            query.user_id, query.page, query.items_per_page
        )

        user_infos = []
        for follow in follows:
            followee: User | None = await self.user_repo.find_by_id(follow.followee_id)
            if not followee:
                continue

            # 요청자와의 팔로우 관계 확인
            is_following: bool = await self.follow_domain_service.is_following(
                requester_id, followee.id
            )
            is_followed_by: bool = await self.follow_domain_service.is_following(
                followee.id, requester_id
            )

            # 팔로우 통계
            stats = await self.follow_domain_service.get_follow_stats(followee.id)

            user_info: UserFollowInfoDTO = UserFollowInfoDTO.create(
                user_id=followee.id,
                username=followee.name.value,
                email=followee.email.value,
                followers_count=stats["followers_count"],
                followees_count=stats["followees_count"],
                is_following=is_following,
                is_followed_by=is_followed_by,
            )
            user_infos.append(user_info)

        return FollowPageDTO.from_domain(
            total_count, query.page, query.items_per_page, user_infos
        )

    async def get_follow_stats(self, user_id: str) -> FollowStatsDTO:
        """팔로우 통계 조회"""
        stats = await self.follow_domain_service.get_follow_stats(user_id)
        return FollowStatsDTO.from_stats(user_id, stats)

    async def check_follow_status(self, follower_id: str, followee_id: str) -> dict:
        """팔로우 상태 확인"""
        is_following: bool = await self.follow_domain_service.is_following(
            follower_id, followee_id
        )
        is_mutual: bool = await self.follow_domain_service.is_mutual_follow(
            follower_id, followee_id
        )

        return {
            "is_following": is_following,
            "is_mutual": is_mutual,
        }

    async def get_follow_suggestions(
        self, user_id: str, limit: int = 10
    ) -> FollowSuggestionsDTO:
        """팔로우 추천 목록 조회"""
        suggested_user_ids: List[str] = await self.follow_repo.get_follow_suggestions(
            user_id, limit
        )

        suggestions = []
        for suggested_id in suggested_user_ids:
            user: User | None = await self.user_repo.find_by_id(suggested_id)
            if not user:
                continue

            stats = await self.follow_domain_service.get_follow_stats(suggested_id)

            user_info: UserFollowInfoDTO = UserFollowInfoDTO.create(
                user_id=user.id,
                username=user.name.value,
                email=user.email.value,
                followers_count=stats["followers_count"],
                followees_count=stats["followees_count"],
                is_following=False,  # 추천 목록이므로 아직 팔로우하지 않음
                is_followed_by=False,
            )
            suggestions.append(user_info)

        return FollowSuggestionsDTO.from_users(suggestions)
