from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entity.bookmark import Bookmark
from app.modules.social.domain.repository.bookmark_repo import IBookmarkRepository
from app.modules.social.infrastructure.db_model.bookmark import BookmarkModel


class BookmarkRepository(IBookmarkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, bookmark_model: BookmarkModel) -> Bookmark:
        """DB Model → Domain Entity 변환"""
        return Bookmark(
            id=bookmark_model.id,
            curriculum_id=bookmark_model.curriculum_id,
            user_id=bookmark_model.user_id,
            created_at=bookmark_model.created_at,
        )

    async def save(self, bookmark: Bookmark) -> None:
        """북마크 저장"""
        new_bookmark = BookmarkModel(  # type: ignore
            id=bookmark.id,
            curriculum_id=bookmark.curriculum_id,
            user_id=bookmark.user_id,
            created_at=bookmark.created_at,
        )
        self.session.add(new_bookmark)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, bookmark_id: str) -> Optional[Bookmark]:
        """ID로 북마크 조회"""
        query: Select[Tuple[BookmarkModel]] = select(BookmarkModel).where(
            BookmarkModel.id == bookmark_id
        )
        result: Result[Tuple[BookmarkModel]] = await self.session.execute(query)
        bookmark_model: BookmarkModel | None = result.scalar_one_or_none()

        if not bookmark_model:
            return None
        return self._to_domain(bookmark_model)

    async def find_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> Optional[Bookmark]:
        """커리큘럼과 사용자로 북마크 조회"""
        query: Select[Tuple[BookmarkModel]] = select(BookmarkModel).where(
            BookmarkModel.curriculum_id == curriculum_id,
            BookmarkModel.user_id == user_id,
        )
        result: Result[Tuple[BookmarkModel]] = await self.session.execute(query)
        bookmark_model: BookmarkModel | None = result.scalar_one_or_none()

        if not bookmark_model:
            return None
        return self._to_domain(bookmark_model)

    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Bookmark]]:
        """사용자의 모든 북마크 조회 (페이징)"""
        base_query: Select[Tuple[BookmarkModel]] = select(BookmarkModel).where(
            BookmarkModel.user_id == user_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[BookmarkModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(BookmarkModel.created_at.desc())
        )

        result: Result[Tuple[BookmarkModel]] = await self.session.execute(paged_query)
        bookmark_models: Sequence[BookmarkModel] = result.scalars().all()

        bookmarks: List[Bookmark] = [
            self._to_domain(model) for model in bookmark_models
        ]
        return total_count, bookmarks

    async def delete(self, bookmark_id: str) -> None:
        """북마크 삭제"""
        query = delete(BookmarkModel).where(BookmarkModel.id == bookmark_id)
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> None:
        """커리큘럼과 사용자로 북마크 삭제"""
        query = delete(BookmarkModel).where(
            BookmarkModel.curriculum_id == curriculum_id,
            BookmarkModel.user_id == user_id,
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def count_by_user(self, user_id: str) -> int:
        """사용자의 북마크 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(BookmarkModel)
            .where(BookmarkModel.user_id == user_id)
        )
        return await self.session.scalar(query) or 0

    async def exists_by_curriculum_and_user(
        self, curriculum_id: str, user_id: str
    ) -> bool:
        """커리큘럼-사용자 북마크 존재 여부 확인"""
        query: Select[Tuple[BookmarkModel]] = select(BookmarkModel).where(
            BookmarkModel.curriculum_id == curriculum_id,
            BookmarkModel.user_id == user_id,
        )
        result: Result[Tuple[BookmarkModel]] = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
