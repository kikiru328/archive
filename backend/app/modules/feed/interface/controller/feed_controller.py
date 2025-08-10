from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.feed.application.service.feed_service import FeedService
from app.modules.feed.application.dto.feed_dto import FeedQuery
from app.modules.feed.interface.schema.feed_schema import FeedPageResponse


feed_router = APIRouter(prefix="/feed", tags=["Social"])


@feed_router.get("/public", response_model=FeedPageResponse)
@inject
async def get_public_feed(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(20, ge=1, le=50, description="페이지당 항목 수"),
    category_id: Optional[str] = Query(None, description="카테고리 ID로 필터링"),
    tags: Optional[str] = Query(None, description="태그로 필터링 (쉼표로 구분)"),
    search: Optional[str] = Query(None, description="제목 또는 작성자로 검색"),
    feed_service: FeedService = Depends(Provide[Container.feed_service]),
) -> FeedPageResponse:
    """공개 커리큘럼 피드 조회"""

    # 태그 파싱
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    query = FeedQuery(
        category_id=category_id,
        tags=tag_list,
        search_query=search,
        page=page,
        items_per_page=items_per_page,
    )

    feed_page = await feed_service.get_public_feed(query)
    return FeedPageResponse.from_dto(feed_page)


@feed_router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def refresh_feed(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    feed_service: FeedService = Depends(Provide[Container.feed_service]),
) -> None:
    """전체 피드 캐시 갱신 (관리자만)"""
    if current_user.role.value != "ADMIN":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    await feed_service.refresh_entire_feed()


@feed_router.post("/refresh/{curriculum_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def refresh_curriculum_feed(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    feed_service: FeedService = Depends(Provide[Container.feed_service]),
) -> None:
    """특정 커리큘럼 피드 아이템 갱신"""
    await feed_service.refresh_feed_item(curriculum_id)
