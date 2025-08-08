from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, func, select, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entity.follow import Follow
from app.modules.social.domain.repository.follow_repo import IFollowRepository
from app.modules.social.infrastructure.db_model.follow import FollowModel


class FollowRepository(IFollowRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, follow_model: FollowModel) -> Follow:
        """DB Model → Domain Entity 변환"""
        return Follow(
            id=follow_model.id,
            follower_id=follow_model.follower_id,
            followee_id=follow_model.followee_id,
            created_at=follow_model.created_at,
        )

    async def save(self, follow: Follow) -> None:
        """팔로우 관계 저장"""
        new_follow = FollowModel(  # type: ignore
            id=follow.id,
            follower_id=follow.follower_id,
            followee_id=follow.followee_id,
            created_at=follow.created_at,
        )
        self.session.add(new_follow)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, follow_id: str) -> Optional[Follow]:
        """ID로 팔로우 관계 조회"""
        query: Select[Tuple[FollowModel]] = select(FollowModel).where(
            FollowModel.id == follow_id
        )
        result: Result[Tuple[FollowModel]] = await self.session.execute(query)
        follow_model: FollowModel | None = result.scalar_one_or_none()

        if not follow_model:
            return None

        return self._to_domain(follow_model)

    async def find_by_follower_and_followee(
        self, follower_id: str, followee_id: str
    ) -> Optional[Follow]:
        """팔로워와 팔로위로 팔로우 관계 조회"""
        query: Select[Tuple[FollowModel]] = select(FollowModel).where(
            and_(
                FollowModel.follower_id == follower_id,
                FollowModel.followee_id == followee_id,
            )
        )
        result: Result[Tuple[FollowModel]] = await self.session.execute(query)
        follow_model: FollowModel | None = result.scalar_one_or_none()

        if not follow_model:
            return None

        return self._to_domain(follow_model)

    async def find_followers(
        self, followee_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Follow]]:
        """특정 사용자의 팔로워 목록 조회 (페이징)"""
        base_query: Select[Tuple[FollowModel]] = select(FollowModel).where(
            FollowModel.followee_id == followee_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[FollowModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(FollowModel.created_at.desc())
        )

        result: Result[Tuple[FollowModel]] = await self.session.execute(paged_query)
        follow_models: Sequence[FollowModel] = result.scalars().all()

        follows: List[Follow] = [self._to_domain(model) for model in follow_models]
        return total_count, follows

    async def find_followees(
        self, follower_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Follow]]:
        """특정 사용자가 팔로우하는 사람들 목록 조회 (페이징)"""
        base_query: Select[Tuple[FollowModel]] = select(FollowModel).where(
            FollowModel.follower_id == follower_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[FollowModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(FollowModel.created_at.desc())
        )

        result: Result[Tuple[FollowModel]] = await self.session.execute(paged_query)
        follow_models: Sequence[FollowModel] = result.scalars().all()

        follows: List[Follow] = [self._to_domain(model) for model in follow_models]
        return total_count, follows

    async def delete(self, follow_id: str) -> None:
        """팔로우 관계 삭제"""
        query = delete(FollowModel).where(FollowModel.id == follow_id)
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_by_follower_and_followee(
        self, follower_id: str, followee_id: str
    ) -> None:
        """팔로워와 팔로위로 팔로우 관계 삭제"""
        query = delete(FollowModel).where(
            and_(
                FollowModel.follower_id == follower_id,
                FollowModel.followee_id == followee_id,
            )
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def count_followers(self, followee_id: str) -> int:
        """특정 사용자의 팔로워 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(FollowModel)
            .where(FollowModel.followee_id == followee_id)
        )
        return await self.session.scalar(query) or 0

    async def count_followees(self, follower_id: str) -> int:
        """특정 사용자가 팔로우하는 사람 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(FollowModel)
            .where(FollowModel.follower_id == follower_id)
        )
        return await self.session.scalar(query) or 0

    async def exists_follow(self, follower_id: str, followee_id: str) -> bool:
        """팔로우 관계 존재 여부 확인"""
        query: Select[Tuple[FollowModel]] = select(FollowModel).where(
            and_(
                FollowModel.follower_id == follower_id,
                FollowModel.followee_id == followee_id,
            )
        )
        result: Result[Tuple[FollowModel]] = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def delete_all_by_user(self, user_id: str) -> None:
        """특정 사용자와 관련된 모든 팔로우 관계 삭제 (계정 삭제시)"""
        query = delete(FollowModel).where(
            or_(
                FollowModel.follower_id == user_id,
                FollowModel.followee_id == user_id,
            )
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def get_mutual_followers(
        self, user1_id: str, user2_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[str]]:
        """두 사용자의 공통 팔로워 목록 조회"""
        # user1의 팔로워들
        user1_followers = select(FollowModel.follower_id).where(  # noqa: F841
            FollowModel.followee_id == user1_id
        )

        # user2의 팔로워들
        user2_followers = select(FollowModel.follower_id).where(  # noqa: F841
            FollowModel.followee_id == user2_id
        )

        # 교집합 쿼리
        base_query = (
            select(FollowModel.follower_id)
            .where(FollowModel.followee_id == user1_id)
            .intersect(
                select(FollowModel.follower_id).where(
                    FollowModel.followee_id == user2_id
                )
            )
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query = base_query.limit(items_per_page).offset(offset)

        result = await self.session.execute(paged_query)
        mutual_follower_ids = result.scalars().all()

        return total_count, list(mutual_follower_ids)

    async def get_follow_suggestions(self, user_id: str, limit: int = 10) -> List[str]:
        """팔로우 추천 사용자 목록 (팔로우하는 사람들의 팔로위 기반)"""
        # 현재 사용자가 팔로우하는 사람들
        my_followees = select(FollowModel.followee_id).where(
            FollowModel.follower_id == user_id
        )

        # 그 사람들이 팔로우하는 사람들 (2차 연결)
        suggestions_query = (
            select(FollowModel.followee_id, func.count().label("count"))
            .where(
                and_(
                    FollowModel.follower_id.in_(my_followees),
                    FollowModel.followee_id != user_id,  # 자기 자신 제외
                    ~FollowModel.followee_id.in_(  # 이미 팔로우 중인 사람들 제외
                        select(FollowModel.followee_id).where(
                            FollowModel.follower_id == user_id
                        )
                    ),
                )
            )
            .group_by(FollowModel.followee_id)
            .order_by(func.count().desc())
            .limit(limit)
        )

        result = await self.session.execute(suggestions_query)
        suggested_users = result.scalars().all()

        return list(suggested_users)
