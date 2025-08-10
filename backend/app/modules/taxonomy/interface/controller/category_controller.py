from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.taxonomy.application.service.category_service import CategoryService
from app.modules.taxonomy.application.dto.tag_dto import CategoryQuery
from app.modules.taxonomy.interface.schema.tag_schema import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
    CategoryResponse,
    CategoryBriefResponse,
    CategoryPageResponse,
    CategoryReorderRequest,
    CategoryStatisticsResponse,
)


category_router = APIRouter(prefix="/categories", tags=["Categories"])


@category_router.post(
    "/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_category(
    request: CreateCategoryRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> CategoryResponse:
    """카테고리 생성 (관리자만)"""
    command = request.to_command()
    dto = await category_service.create_category(
        command, current_user.id, current_user.role
    )
    return CategoryResponse.from_dto(dto)


@category_router.get("/active", response_model=list[CategoryBriefResponse])
@inject
async def get_active_categories(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> list[CategoryBriefResponse]:
    """활성화된 카테고리 목록 조회"""
    categories = await category_service.get_active_categories()
    return [CategoryBriefResponse.from_dto(category) for category in categories]


@category_router.get("/", response_model=CategoryPageResponse)
@inject
async def get_categories(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(20, ge=1, le=50, description="페이지당 항목 수"),
    include_inactive: bool = Query(False, description="비활성화된 카테고리 포함 여부"),
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> CategoryPageResponse:
    """카테고리 목록 조회"""
    query = CategoryQuery(
        page=page,
        items_per_page=items_per_page,
        include_inactive=include_inactive,
    )
    page_dto = await category_service.get_categories(query)
    return CategoryPageResponse.from_dto(page_dto)


@category_router.get("/statistics", response_model=CategoryStatisticsResponse)
@inject
async def get_category_statistics(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> CategoryStatisticsResponse:
    """카테고리 통계 조회"""
    stats = await category_service.get_category_statistics()
    return CategoryStatisticsResponse(
        total_categories=stats.total_categories,
        active_categories=stats.active_categories,
        inactive_categories=stats.inactive_categories,
    )


@category_router.get("/{category_id}", response_model=CategoryResponse)
@inject
async def get_category_by_id(
    category_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> CategoryResponse:
    """ID로 카테고리 상세 조회"""
    dto = await category_service.get_category_by_id(
        category_id, current_user.id, current_user.role
    )
    return CategoryResponse.from_dto(dto)


@category_router.patch("/{category_id}", response_model=CategoryResponse)
@inject
async def update_category(
    category_id: str,
    request: UpdateCategoryRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> CategoryResponse:
    """카테고리 수정 (관리자만)"""
    command = request.to_command(category_id)
    dto = await category_service.update_category(
        command, current_user.id, current_user.role
    )
    return CategoryResponse.from_dto(dto)


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_category(
    category_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> None:
    """카테고리 삭제 (관리자만)"""
    await category_service.delete_category(
        category_id, current_user.id, current_user.role
    )


@category_router.post("/{category_id}/activate", response_model=CategoryResponse)
@inject
async def activate_category(
    category_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> CategoryResponse:
    """카테고리 활성화 (관리자만)"""
    dto = await category_service.activate_category(
        category_id, current_user.id, current_user.role
    )
    return CategoryResponse.from_dto(dto)


@category_router.post("/{category_id}/deactivate", response_model=CategoryResponse)
@inject
async def deactivate_category(
    category_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> CategoryResponse:
    """카테고리 비활성화 (관리자만)"""
    dto = await category_service.deactivate_category(
        category_id, current_user.id, current_user.role
    )
    return CategoryResponse.from_dto(dto)


@category_router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def reorder_categories(
    request: CategoryReorderRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    category_service: CategoryService = Depends(Provide[Container.category_service]),
) -> None:
    """카테고리 순서 재정렬 (관리자만)"""
    category_orders = [(item.id, item.sort_order) for item in request.categories]
    await category_service.reorder_categories(
        category_orders, current_user.id, current_user.role
    )
