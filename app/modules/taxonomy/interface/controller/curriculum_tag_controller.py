from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.taxonomy.application.service.curriculum_tag_service import (
    CurriculumTagService,
)
from app.modules.taxonomy.application.dto.tag_dto import (
    AddTagsToCurriculumCommand,
    CategoryDTO,
    CurriculumTagsDTO,
    RemoveTagFromCurriculumCommand,
    AssignCategoryToCurriculumCommand,
    TagDTO,
)
from app.modules.taxonomy.interface.schema.tag_schema import (
    AddTagsRequest,
    RemoveTagRequest,
    AssignCategoryRequest,
    CurriculumTagsResponse,
    TagBriefResponse,
    CategoryBriefResponse,
)
from app.modules.user.domain.vo.role import RoleVO


taxonomy_router = APIRouter(prefix="/curriculums", tags=["Taxonomies"])


@taxonomy_router.post(
    "/{curriculum_id}/tags",
    response_model=List[TagBriefResponse],
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_tags_to_curriculum(
    curriculum_id: str,
    request: AddTagsRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> List[TagBriefResponse]:
    """커리큘럼에 태그 추가"""
    command: AddTagsToCurriculumCommand = request.to_command(
        curriculum_id, current_user.id
    )
    tag_dtos: List[TagDTO] = await curriculum_tag_service.add_tags_to_curriculum(
        command, RoleVO(current_user.role)
    )
    return [TagBriefResponse.from_dto(tag) for tag in tag_dtos]


@taxonomy_router.delete(
    "/{curriculum_id}/tags",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def remove_tag_from_curriculum(
    curriculum_id: str,
    request: RemoveTagRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> None:
    """커리큘럼에서 태그 제거"""
    command: RemoveTagFromCurriculumCommand = request.to_command(curriculum_id)
    await curriculum_tag_service.remove_tag_from_curriculum(
        command, current_user.id, RoleVO(current_user.role)
    )


@taxonomy_router.post(
    "/{curriculum_id}/category",
    response_model=CategoryBriefResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def assign_category_to_curriculum(
    curriculum_id: str,
    request: AssignCategoryRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> CategoryBriefResponse:
    """커리큘럼에 카테고리 할당"""
    command: AssignCategoryToCurriculumCommand = request.to_command(
        curriculum_id, current_user.id
    )
    category_dto: CategoryDTO = (
        await curriculum_tag_service.assign_category_to_curriculum(
            command, RoleVO(current_user.role)
        )
    )
    return CategoryBriefResponse.from_dto(category_dto)


@taxonomy_router.delete(
    "/{curriculum_id}/category",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def remove_category_from_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> None:
    """커리큘럼에서 카테고리 제거"""
    await curriculum_tag_service.remove_category_from_curriculum(
        curriculum_id, current_user.id, RoleVO(current_user.role)
    )


@taxonomy_router.get(
    "/{curriculum_id}/tags-and-category",
    response_model=CurriculumTagsResponse,
)
@inject
async def get_curriculum_tags_and_category(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> CurriculumTagsResponse:
    """커리큘럼의 태그와 카테고리 조회"""
    curriculum_tags_dto: CurriculumTagsDTO = (
        await curriculum_tag_service.get_curriculum_tags_and_category(
            curriculum_id, current_user.id, RoleVO(current_user.role)
        )
    )
    return CurriculumTagsResponse.from_dto(curriculum_tags_dto)


# ========================= 검색 및 발견 엔드포인트 =========================


@taxonomy_router.get(
    "/search/by-tags",
    response_model=List[str],
)
@inject
async def find_curriculums_by_tags(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    tag_names: List[str] = Query(..., description="검색할 태그 이름들"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> List[str]:
    """태그로 커리큘럼 검색"""
    total_count, curriculum_ids = await curriculum_tag_service.find_curriculums_by_tags(
        tag_names, page, items_per_page
    )
    return curriculum_ids


@taxonomy_router.get(
    "/search/by-category/{category_id}",
    response_model=List[str],
)
@inject
async def find_curriculums_by_category(
    category_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> List[str]:
    """카테고리로 커리큘럼 검색"""
    total_count, curriculum_ids = (
        await curriculum_tag_service.find_curriculums_by_category(
            category_id, page, items_per_page
        )
    )
    return curriculum_ids


# ========================= 사용자 활동 조회 엔드포인트 =========================


@taxonomy_router.get(
    "/tags/my-tagged-curriculums",
    response_model=List[str],
)
@inject
async def get_my_tagged_curriculums(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> List[str]:
    """내가 태그를 추가한 커리큘럼 목록 조회"""
    total_count, curriculum_ids = (
        await curriculum_tag_service.get_user_tagged_curriculums(
            current_user.id, page, items_per_page
        )
    )
    return curriculum_ids


@taxonomy_router.get(
    "/categories/my-categorized-curriculums",
    response_model=List[str],
)
@inject
async def get_my_categorized_curriculums(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    curriculum_tag_service: CurriculumTagService = Depends(
        Provide[Container.curriculum_tag_service]
    ),
) -> List[str]:
    """내가 카테고리를 할당한 커리큘럼 목록 조회"""
    total_count, curriculum_ids = (
        await curriculum_tag_service.get_user_categorized_curriculums(
            current_user.id, page, items_per_page
        )
    )
    return curriculum_ids
