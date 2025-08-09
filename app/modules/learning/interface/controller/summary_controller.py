from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.learning.application.service.summary_service import SummaryService
from app.modules.learning.application.dto.learning_dto import (
    CreateSummaryCommand,
    SummaryQuery,
    SummaryDTO,
    SummaryPageDTO,
)
from app.modules.learning.interface.schema.summary_schema import (
    CreateSummaryRequest,
    UpdateSummaryRequest,
    SummaryResponse,
    SummaryPageResponse,
)
from app.modules.user.domain.vo.role import RoleVO


summary_router = APIRouter(prefix="/curriculums", tags=["Summaries"])


@summary_router.post(
    "/{curriculum_id}/weeks/{week_number}/summaries",
    response_model=SummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_summary(
    curriculum_id: str,
    week_number: int,
    request: CreateSummaryRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    summary_service: SummaryService = Depends(Provide[Container.summary_service]),
) -> SummaryResponse:
    """요약 생성"""
    command: CreateSummaryCommand = request.to_command(
        curriculum_id=curriculum_id,
        week_number=week_number,
        owner_id=current_user.id,
    )

    dto: SummaryDTO = await summary_service.create_summary(
        command=command,
        role=RoleVO(current_user.role.value),
    )

    return SummaryResponse.from_dto(dto)


@summary_router.get(
    "/{curriculum_id}/weeks/{week_number}/summaries",
    response_model=SummaryPageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_summaries_by_curriculum_and_week(
    curriculum_id: str,
    week_number: int,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    summary_service: SummaryService = Depends(Provide[Container.summary_service]),
) -> SummaryPageResponse:
    """특정 커리큘럼의 특정 주차 요약 목록 조회"""
    query = SummaryQuery(
        curriculum_id=curriculum_id,
        week_number=week_number,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: SummaryPageDTO = await summary_service.get_summaries(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return SummaryPageResponse.from_dto(page_dto)


@summary_router.get(
    "/{curriculum_id}/summaries",
    response_model=SummaryPageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_summaries_by_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    summary_service: SummaryService = Depends(Provide[Container.summary_service]),
) -> SummaryPageResponse:
    """특정 커리큘럼의 모든 요약 목록 조회"""
    query = SummaryQuery(
        curriculum_id=curriculum_id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: SummaryPageDTO = await summary_service.get_summaries(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return SummaryPageResponse.from_dto(page_dto)


@summary_router.get(
    "/summaries/{summary_id}",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_summary_by_id(
    summary_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    summary_service: SummaryService = Depends(Provide[Container.summary_service]),
) -> SummaryResponse:
    """ID로 요약 상세 조회"""
    dto: SummaryDTO = await summary_service.get_summary_by_id(
        summary_id=summary_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return SummaryResponse.from_dto(dto)


@summary_router.put(
    "/summaries/{summary_id}",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_summary(
    summary_id: str,
    request: UpdateSummaryRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    summary_service: SummaryService = Depends(Provide[Container.summary_service]),
) -> SummaryResponse:
    """요약 수정"""
    command = request.to_command(
        summary_id=summary_id,
        owner_id=current_user.id,
    )

    dto: SummaryDTO = await summary_service.update_summary(
        command=command,
        role=RoleVO(current_user.role.value),
    )

    return SummaryResponse.from_dto(dto)


@summary_router.delete(
    "/summaries/{summary_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_summary(
    summary_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    summary_service: SummaryService = Depends(Provide[Container.summary_service]),
) -> None:
    """요약 삭제"""
    await summary_service.delete_summary(
        summary_id=summary_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )


user_summary_router = APIRouter(prefix="/users/me/summaries", tags=["Users"])


@user_summary_router.get(
    "", response_model=SummaryPageResponse, status_code=status.HTTP_200_OK
)
@inject
async def get_my_summaries(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    summary_service: SummaryService = Depends(Provide[Container.summary_service]),
) -> SummaryPageResponse:
    """내가 작성한 모든 요약 목록 조회"""
    query = SummaryQuery(
        owner_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: SummaryPageDTO = await summary_service.get_summaries(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return SummaryPageResponse.from_dto(page_dto)
