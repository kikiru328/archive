from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entity.comment import Comment
from app.modules.social.domain.repository.comment_repo import ICommentRepository
from app.modules.social.domain.vo.comment_content import CommentContent
from app.modules.social.infrastructure.db_model.comment import CommentModel


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, comment_model: CommentModel) -> Comment:
        """DB Model → Domain Entity 변환"""
        return Comment(
            id=comment_model.id,
            curriculum_id=comment_model.curriculum_id,
            user_id=comment_model.user_id,
            content=CommentContent(comment_model.content),
            created_at=comment_model.created_at,
            updated_at=comment_model.updated_at,
        )

    async def save(self, comment: Comment) -> None:
        """댓글 저장"""
        new_comment = CommentModel(  # type: ignore
            id=comment.id,
            curriculum_id=comment.curriculum_id,
            user_id=comment.user_id,
            content=comment.content.value,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
        self.session.add(new_comment)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, comment_id: str) -> Optional[Comment]:
        """ID로 댓글 조회"""
        query: Select[Tuple[CommentModel]] = select(CommentModel).where(
            CommentModel.id == comment_id
        )
        result: Result[Tuple[CommentModel]] = await self.session.execute(query)
        comment_model: CommentModel | None = result.scalar_one_or_none()

        if not comment_model:
            return None
        return self._to_domain(comment_model)

    async def find_by_curriculum(
        self, curriculum_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Comment]]:
        """커리큘럼의 모든 댓글 조회 (페이징)"""
        base_query: Select[Tuple[CommentModel]] = select(CommentModel).where(
            CommentModel.curriculum_id == curriculum_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[CommentModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CommentModel.created_at.desc())
        )

        result: Result[Tuple[CommentModel]] = await self.session.execute(paged_query)
        comment_models: Sequence[CommentModel] = result.scalars().all()

        comments: List[Comment] = [self._to_domain(model) for model in comment_models]
        return total_count, comments

    async def find_by_user(
        self, user_id: str, page: int = 1, items_per_page: int = 10
    ) -> Tuple[int, List[Comment]]:
        """사용자의 모든 댓글 조회 (페이징)"""
        base_query: Select[Tuple[CommentModel]] = select(CommentModel).where(
            CommentModel.user_id == user_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[CommentModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(CommentModel.created_at.desc())
        )

        result: Result[Tuple[CommentModel]] = await self.session.execute(paged_query)
        comment_models: Sequence[CommentModel] = result.scalars().all()

        comments: List[Comment] = [self._to_domain(model) for model in comment_models]
        return total_count, comments

    async def update(self, comment: Comment) -> None:
        """댓글 업데이트"""
        existing_comment: CommentModel | None = await self.session.get(
            CommentModel, comment.id
        )
        if not existing_comment:
            raise ValueError(f"Comment {comment.id} not found")

        existing_comment.content = comment.content.value
        existing_comment.updated_at = comment.updated_at

        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete(self, comment_id: str) -> None:
        """댓글 삭제"""
        query = delete(CommentModel).where(CommentModel.id == comment_id)
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def count_by_curriculum(self, curriculum_id: str) -> int:
        """커리큘럼의 댓글 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(CommentModel)
            .where(CommentModel.curriculum_id == curriculum_id)
        )
        return await self.session.scalar(query) or 0

    async def count_by_user(self, user_id: str) -> int:
        """사용자의 댓글 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(CommentModel)
            .where(CommentModel.user_id == user_id)
        )
        return await self.session.scalar(query) or 0
