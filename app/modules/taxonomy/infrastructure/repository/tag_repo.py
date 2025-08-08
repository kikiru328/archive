from datetime import datetime, timezone
from typing import List, Optional, Sequence, Tuple
from sqlalchemy import Result, Select, func, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID  # type: ignore

from app.modules.taxonomy.domain.entity.tag import Tag
from app.modules.taxonomy.domain.repository.tag_repo import ITagRepository
from app.modules.taxonomy.domain.vo.tag_name import TagName
from app.modules.taxonomy.infrastructure.db_model.tag import TagModel


class TagRepository(ITagRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, tag_model: TagModel) -> Tag:
        """DB Model → Domain Entity 변환"""
        return Tag(
            id=tag_model.id,
            name=TagName(tag_model.name),
            usage_count=tag_model.usage_count,
            created_by=tag_model.created_by,
            created_at=tag_model.created_at,
            updated_at=tag_model.updated_at,
        )

    async def save(self, tag: Tag) -> None:
        """태그 저장"""
        new_tag = TagModel(  # type: ignore
            id=tag.id,
            name=tag.name.value,
            usage_count=tag.usage_count,
            created_by=tag.created_by,
            created_at=tag.created_at,
            updated_at=tag.updated_at,
        )
        self.session.add(new_tag)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, tag_id: str) -> Optional[Tag]:
        """ID로 태그 조회"""
        query: Select[Tuple[TagModel]] = select(TagModel).where(TagModel.id == tag_id)
        result: Result[Tuple[TagModel]] = await self.session.execute(query)
        tag_model: TagModel | None = result.scalar_one_or_none()

        if not tag_model:
            return None

        return self._to_domain(tag_model)

    async def find_by_name(self, name: TagName) -> Optional[Tag]:
        """이름으로 태그 조회"""
        query: Select[Tuple[TagModel]] = select(TagModel).where(
            TagModel.name == name.value
        )
        result: Result[Tuple[TagModel]] = await self.session.execute(query)
        tag_model: TagModel | None = result.scalar_one_or_none()

        if not tag_model:
            return None

        return self._to_domain(tag_model)

    async def find_or_create_by_names(
        self, tag_names: List[TagName], created_by: str
    ) -> List[Tag]:
        """태그 이름 리스트로 태그들을 찾거나 생성"""
        tags = []
        now = datetime.now(timezone.utc)

        for tag_name in tag_names:
            # 기존 태그 찾기
            existing_tag = await self.find_by_name(tag_name)

            if existing_tag:
                tags.append(existing_tag)
            else:
                # 새 태그 생성
                new_tag = Tag(
                    id=ULID().generate(),
                    name=tag_name,
                    usage_count=0,
                    created_by=created_by,
                    created_at=now,
                    updated_at=now,
                )
                await self.save(new_tag)
                tags.append(new_tag)

        return tags

    async def find_popular_tags(self, limit: int = 20, min_usage: int = 1) -> List[Tag]:
        """인기 태그 조회 (사용횟수 기준)"""
        query: Select[Tuple[TagModel]] = (
            select(TagModel)
            .where(TagModel.usage_count >= min_usage)
            .order_by(TagModel.usage_count.desc())
            .limit(limit)
        )

        result: Result[Tuple[TagModel]] = await self.session.execute(query)
        tag_models: Sequence[TagModel] = result.scalars().all()

        return [self._to_domain(model) for model in tag_models]

    async def search_by_name(self, query: str, limit: int = 10) -> List[Tag]:
        """태그 이름으로 검색 (자동완성용)"""
        search_query: Select[Tuple[TagModel]] = (
            select(TagModel)
            .where(TagModel.name.like(f"%{query.lower()}%"))
            .order_by(TagModel.usage_count.desc())
            .limit(limit)
        )

        result: Result[Tuple[TagModel]] = await self.session.execute(search_query)
        tag_models: Sequence[TagModel] = result.scalars().all()

        return [self._to_domain(model) for model in tag_models]

    async def find_all(
        self, page: int = 1, items_per_page: int = 20
    ) -> Tuple[int, List[Tag]]:
        """모든 태그 조회 (페이징)"""
        base_query: Select[Tuple[TagModel]] = select(TagModel)

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[TagModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(TagModel.usage_count.desc(), TagModel.name.asc())
        )

        result: Result[Tuple[TagModel]] = await self.session.execute(paged_query)
        tag_models: Sequence[TagModel] = result.scalars().all()

        tags: List[Tag] = [self._to_domain(model) for model in tag_models]
        return total_count, tags

    async def find_by_creator(
        self, creator_id: str, page: int = 1, items_per_page: int = 20
    ) -> Tuple[int, List[Tag]]:
        """생성자별 태그 조회 (페이징)"""
        base_query: Select[Tuple[TagModel]] = select(TagModel).where(
            TagModel.created_by == creator_id
        )

        # 총 개수 조회
        count_query: Select[Tuple[int]] = select(func.count()).select_from(
            base_query.subquery()
        )
        total_count: int = await self.session.scalar(count_query) or 0

        # 페이지네이션
        offset: int = (page - 1) * items_per_page
        paged_query: Select[Tuple[TagModel]] = (
            base_query.limit(items_per_page)
            .offset(offset)
            .order_by(TagModel.created_at.desc())
        )

        result: Result[Tuple[TagModel]] = await self.session.execute(paged_query)
        tag_models: Sequence[TagModel] = result.scalars().all()

        tags: List[Tag] = [self._to_domain(model) for model in tag_models]
        return total_count, tags

    async def update(self, tag: Tag) -> None:
        """태그 업데이트"""
        existing_tag: TagModel | None = await self.session.get(TagModel, tag.id)
        if not existing_tag:
            raise ValueError(f"Tag {tag.id} not found")

        existing_tag.name = tag.name.value
        existing_tag.usage_count = tag.usage_count
        existing_tag.updated_at = tag.updated_at

        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete(self, tag_id: str) -> None:
        """태그 삭제"""
        query = delete(TagModel).where(TagModel.id == tag_id)
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def increment_usage_count(self, tag_id: str) -> None:
        """태그 사용 횟수 증가"""
        query = (
            update(TagModel)
            .where(TagModel.id == tag_id)
            .values(
                usage_count=TagModel.usage_count + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def decrement_usage_count(self, tag_id: str) -> None:
        """태그 사용 횟수 감소"""
        query = (
            update(TagModel)
            .where(TagModel.id == tag_id)
            .values(
                usage_count=func.greatest(
                    TagModel.usage_count - 1, 0
                ),  # 0 이하로 내려가지 않음
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(query)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def exists_by_name(self, name: TagName) -> bool:
        """태그 이름으로 존재 여부 확인"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(TagModel)
            .where(TagModel.name == name.value)
        )
        count: int = await self.session.scalar(query) or 0
        return count > 0

    async def count_all(self) -> int:
        """전체 태그 수 조회"""
        query: Select[Tuple[int]] = select(func.count()).select_from(TagModel)
        return await self.session.scalar(query) or 0

    async def count_by_usage_range(self, min_usage: int, max_usage: int) -> int:
        """사용 횟수 범위별 태그 수 조회"""
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(TagModel)
            .where(TagModel.usage_count.between(min_usage, max_usage))
        )
        return await self.session.scalar(query) or 0
