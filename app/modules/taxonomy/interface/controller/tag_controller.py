from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.taxonomy.application.service.tag_service import TagService
from app.modules.taxonomy.application.dto.tag_dto import (
    CreateTagCommand,
    TagDTO,
    TagQuery,
)
from app.modules.taxonomy.interface.schema.tag_schema import (
    CreateTagRequest,
    UpdateTagRequest,
    TagResponse,
    TagBriefResponse,
    TagPageResponse,
    TagSearchResponse,
    TagStatisticsResponse,
)


tag_router = APIRouter(prefix="/tags", tags=["Tags"])


@tag_router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_tag(
    request: CreateTagRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> TagResponse:
    """태그 생성"""
    command: CreateTagCommand = request.to_command(created_by=current_user.id)
    dto: TagDTO = await tag_service.create_tag(command)
    return TagResponse.from_dto(dto)


@tag_router.get("/popular", response_model=list[TagBriefResponse])
@inject
async def get_popular_tags(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=50, description="조회할 태그 수"),
    min_usage: int = Query(1, ge=1, description="최소 사용 횟수"),
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> list[TagBriefResponse]:
    """인기 태그 목록 조회"""
    tags = await tag_service.get_popular_tags(limit=limit, min_usage=min_usage)
    return [TagBriefResponse.from_dto(tag) for tag in tags]


@tag_router.get("/search", response_model=TagSearchResponse)
@inject
async def search_tags(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    q: str = Query(..., min_length=1, description="검색 쿼리"),
    limit: int = Query(10, ge=1, le=20, description="조회할 태그 수"),
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> TagSearchResponse:
    """태그 검색 (자동완성용)"""
    tags = await tag_service.search_tags(query=q, limit=limit)
    return TagSearchResponse.from_dto_list(tags)


@tag_router.get("/", response_model=TagPageResponse)
@inject
async def get_tags(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(20, ge=1, le=50, description="페이지당 항목 수"),
    search: str = Query(None, description="검색어"),
    min_usage: int = Query(1, ge=0, description="최소 사용 횟수"),
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> TagPageResponse:
    """태그 목록 조회"""
    query = TagQuery(
        page=page,
        items_per_page=items_per_page,
        search_query=search,
        min_usage=min_usage,
    )
    page_dto = await tag_service.get_tags(query)
    return TagPageResponse.from_dto(page_dto)


@tag_router.get("/statistics", response_model=TagStatisticsResponse)
@inject
async def get_tag_statistics(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> TagStatisticsResponse:
    """태그 통계 조회"""
    stats = await tag_service.get_tag_statistics()
    return TagStatisticsResponse(
        total_tags=stats.total_tags,
        popular_tags_count=stats.popular_tags_count,
        unused_tags_count=stats.unused_tags_count,
        most_popular_tags=stats.most_popular_tags,
    )


@tag_router.get("/{tag_id}", response_model=TagResponse)
@inject
async def get_tag_by_id(
    tag_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> TagResponse:
    """ID로 태그 상세 조회"""
    dto = await tag_service.get_tag_by_id(tag_id, current_user.id, current_user.role)
    return TagResponse.from_dto(dto)


@tag_router.patch("/{tag_id}", response_model=TagResponse)
@inject
async def update_tag(
    tag_id: str,
    request: UpdateTagRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> TagResponse:
    """태그 수정"""
    command = request.to_command(tag_id)
    dto = await tag_service.update_tag(command, current_user.id, current_user.role)
    return TagResponse.from_dto(dto)


@tag_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_tag(
    tag_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    tag_service: TagService = Depends(Provide[Container.tag_service]),
) -> None:
    """태그 삭제 (관리자만)"""
    await tag_service.delete_tag(tag_id, current_user.id, current_user.role)
