from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.auth import assert_admin
from app.core.di_container import Container

from app.modules.admin.application.service.admin_curriculum_service import (
    AdminCurriculumService,
)
from app.modules.admin.interface.schema.admin_curriculum_schema import (
    AdminListCurriculumsQuery,
    AdminUpdateCurriculumVisibilityBody,
    AdminGetCurriculumResponse,
    AdminGetCurriculumsPageResponse,
)

admin_curriculum_router = APIRouter(prefix="/admin/curriculums", tags=["Admin"])


@admin_curriculum_router.get(
    "", response_model=AdminGetCurriculumsPageResponse, status_code=status.HTTP_200_OK
)
@inject
async def list_curriculums(
    query: Annotated[AdminListCurriculumsQuery, Depends()],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: AdminCurriculumService = Depends(Provide[Container.admin_curriculum_service]),
) -> AdminGetCurriculumsPageResponse:
    assert_admin(current_user)
    return await svc.list_curriculums(
        page=query.page, items_per_page=query.items_per_page, owner_id=query.owner_id
    )


@admin_curriculum_router.get(
    "/{curriculum_id}",
    response_model=AdminGetCurriculumResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: AdminCurriculumService = Depends(Provide[Container.admin_curriculum_service]),
) -> AdminGetCurriculumResponse:
    assert_admin(current_user)
    try:
        return await svc.get_curriculum(curriculum_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Curriculum not found")


@admin_curriculum_router.patch(
    "/{curriculum_id}/visibility",
    response_model=AdminGetCurriculumResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def change_visibility(
    curriculum_id: str,
    body: AdminUpdateCurriculumVisibilityBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: AdminCurriculumService = Depends(Provide[Container.admin_curriculum_service]),
) -> AdminGetCurriculumResponse:
    assert_admin(current_user)
    try:
        return await svc.change_visibility(curriculum_id, body.visibility)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@admin_curriculum_router.delete(
    "/{curriculum_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: AdminCurriculumService = Depends(Provide[Container.admin_curriculum_service]),
) -> None:
    assert_admin(current_user)
    await svc.delete_curriculum(curriculum_id)
    return
