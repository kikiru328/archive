from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entity.like import Like
from app.modules.social.domain.repository.like_repo import ILikeRepository
from app.modules.social.infrastructure.db_model.like import LikeModel


class LikeRepository(ILikeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, like_model: LikeModel) -> Like:
        """DB Model → Domain Entity 변환"""
        return Like(
            id=like_model.id,
            curriculum_id=like_model.curriculum_id,
            user_id=like_model.user_id,
            created_at=like_model.created_at,
        )

    async def save(self, like: Like) -> None:
        """좋아요 저장"""
        new_like = LikeModel(  # type: ignore
            id=like.id,
            curriculum_id=like.curriculum_id,
            user_id=like.user_id,
            created_at=like.created_at,
        )
        self.session.add(new_like)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, like_id: str) -> Optional[Like]:
        """ID로 좋아요 조회"""
        query: Select[Tuple[LikeModel]] = select(LikeModel).where(
            LikeModel.id == like_id
        )
        result: Result[Tuple[LikeModel]] = await self.session.execute(query)
        like_model: LikeModel | None = result.scalar_one_or_none()

        if not like_model:
            return None
        return self._to_domain(like_model)

    async def find_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> Optional[Like]:
        """커리큘럼과 사용자로 좋아요 조회"""
        query: Select[Tuple[LikeModel]] = select(LikeModel).where(
            LikeModel.curriculum_id == curriculum_id,
            LikeModel.user_id == user_id,
        )
        result: Result[Tuple[LikeModel]] = await self.session.execute(query)
        like_model: LikeModel | None = result.scalar_one_or_none()

        if not like_model:
            return None
        return self._to_domain(like_model)

    async def find_by_curriculum(
        self, curriculum_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Like]]:
        """커리큘럼의 모든 좋아요 조회 (페이징)"""
        base_query: Select[Tuple[LikeModel]] = select(LikeModel).where(
            LikeModel.curriculum_id == curriculum_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[LikeModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(LikeModel.created_at.desc())
        )

        result: Result[Tuple[LikeModel]] = await self.session.execute(paged_query)
        like_models: Sequence[LikeModel] = result.scalars().all()

        likes: List[Like] = [self._to_domain(model) for model in like_models]
        return total_count, likes

    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Like]]:
        """사용자의 모든 좋아요 조회 (페이징)"""
        base_query: Select[Tuple[LikeModel]] = select(LikeModel).where(
            LikeModel.user_id == user_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[LikeModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(LikeModel.created_at.desc())
        )

        result: Result[Tuple[LikeModel]] = await self.session.execute(paged_query)
        like_models: Sequence[LikeModel] = result.scalars().all()

        likes: List[Like] = [self._to_domain(model) for model in like_models]
        return total_count, likes

    async def delete(self, like_id: str) -> None:
        """좋아요 삭제"""
        query = delete(LikeModel).where(LikeModel.id == like_id)
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> None:
        """커리큘럼과 사용자로 좋아요 삭제"""
        query = delete(LikeModel).where(
            LikeModel.curriculum_id == curriculum_id,
            LikeModel.user_id == user_id,
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 좋아요 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(LikeModel)
            .where(LikeModel.curriculum_id == curriculum_id)
        )
        return await self.session.scalar(query) or 0

    async def count_by_user(self, user_id: str) -> int:
        """사용자의 좋아요 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(LikeModel)
            .where(LikeModel.user_id == user_id)
        )
        return await self.session.scalar(query) or 0

    async def exists_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> bool:
        """커리큘럼-사용자 좋아요 존재 여부 확인"""
        query: Select[Tuple[LikeModel]] = select(LikeModel).where(
            LikeModel.curriculum_id == curriculum_id,
            LikeModel.user_id == user_id,
        )
        result: Result[Tuple[LikeModel]] = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
