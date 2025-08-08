from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide
from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.curriculum.application.dto.curriculum_dto import (
    CreateCurriculumCommand,
    CreateLessonCommand,
    CreateWeekScheduleCommand,
    CurriculumDTO,
    CurriculumPageDTO,
    CurriculumQuery,
    DeleteLessonCommand,
    GenerateCurriculumCommand,
    UpdateCurriculumCommand,
    UpdateLessonCommand,
)
from app.modules.curriculum.application.service.curriculum_service import (
    CurriculumService,
)
from app.modules.curriculum.interface.schema.curriculum_schema import (
    CreateCurriculumRequest,
    CreateLessonRequest,
    CreateWeekScheduleRequest,
    CurriculumResponse,
    CurriculumsPageResponse,
    GenerateCurriculumRequest,
    UpdateCurriculumRequest,
    UpdateLessonRequest,
)
from app.modules.user.domain.vo.role import RoleVO


curriculum_router = APIRouter(prefix="/curriculums", tags=["Curriculums"])


@curriculum_router.post(
    "", response_model=CurriculumResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_curriculum(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CreateCurriculumRequest,
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumResponse:

    dto: CreateCurriculumCommand = body.to_dto(owner_id=current_user.id)
    created: CurriculumDTO = await curriculum_service.create_curriculum(dto)
    return CurriculumResponse.from_dto(created)


@curriculum_router.post(
    "/generate", response_model=CurriculumResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def generate_curriculum(
    body: GenerateCurriculumRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumResponse:

    dto: GenerateCurriculumCommand = body.to_dto(owner_id=current_user.id)
    generated: CurriculumDTO = await curriculum_service.generate_curriculum(dto)
    return CurriculumResponse.from_dto(generated)


@curriculum_router.get("/me", response_model=CurriculumsPageResponse)
@inject
async def get_list_my_curriculums(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=100),
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumsPageResponse:
    query = CurriculumQuery(
        owner_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )
    page_dto: CurriculumPageDTO = await curriculum_service.get_curriculums(query=query)
    return CurriculumsPageResponse.from_dto(page_dto)


@curriculum_router.get("/public", response_model=CurriculumsPageResponse)
@inject
async def get_list_public_curriculums(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=100),
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumsPageResponse:
    query = CurriculumQuery(
        owner_id=None,
        page=page,
        items_per_page=items_per_page,
    )
    page_dto: CurriculumPageDTO = await curriculum_service.get_curriculums(query=query)
    return CurriculumsPageResponse.from_dto(page_dto)


@curriculum_router.get("/following", response_model=CurriculumsPageResponse)
@inject
async def get_following_users_curriculums(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=100),
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumsPageResponse:
    """팔로우한 사용자들의 공개 커리큘럼 목록 조회"""
    page_dto: CurriculumPageDTO = (
        await curriculum_service.get_following_users_curriculums(
            user_id=current_user.id,
            page=page,
            items_per_page=items_per_page,
        )
    )
    return CurriculumsPageResponse.from_dto(page_dto)


@curriculum_router.get(
    "/{curriculum_id}",
    response_model=CurriculumResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumResponse:

    role: RoleVO = RoleVO(current_user.role.value) if current_user else RoleVO.USER
    owner_id: str | None = current_user.id if current_user else None
    result: CurriculumDTO = await curriculum_service.get_curriculum_by_id(
        curriculum_id=curriculum_id, role=role, owner_id=owner_id
    )
    return CurriculumResponse.from_dto(result)


@curriculum_router.patch(
    "/{curriculum_id}",
    response_model=CurriculumResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_curriculum(
    curriculum_id: str,
    body: UpdateCurriculumRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumResponse:

    dto: UpdateCurriculumCommand = body.to_dto(
        curriculum_id=curriculum_id, owner_id=current_user.id
    )
    role = RoleVO(current_user.role.value)

    result = await curriculum_service.update_curriculum(command=dto, role=role)

    return CurriculumResponse.from_dto(result)


@curriculum_router.delete("/{curriculum_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> None:

    await curriculum_service.delete_curriculum(
        curriculum_id=curriculum_id,
        owner_id=current_user.id,
        role=RoleVO(current_user.role),
    )


week_router = APIRouter(prefix="/curriculums", tags=["Weeks"])


@week_router.post(
    "/{curriculum_id}/weeks",
    response_model=CurriculumResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_week_schedule(
    curriculum_id: str,
    body: CreateWeekScheduleRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumResponse:

    dto: CreateWeekScheduleCommand = body.to_dto(
        curriculum_id, owner_id=current_user.id
    )
    updated: CurriculumDTO = await curriculum_service.create_week_schedule(
        command=dto,
        role=RoleVO(current_user.role),
    )
    return CurriculumResponse.from_dto(updated)


@week_router.delete(
    "/{curriculum_id}/weeks/{week_number}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_week(
    curriculum_id: str,
    week_number: int,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> None:

    await curriculum_service.delete_week_schedule(
        curriculum_id=curriculum_id,
        owner_id=current_user.id,
        week_number=week_number,
        role=RoleVO(current_user.role),
    )


lesson_router = APIRouter(prefix="/curriculums", tags=["Lessons"])


@lesson_router.post(
    "/{curriculum_id}/weeks/{week_number}/lessons",
    response_model=CurriculumResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_lesson(
    curriculum_id: str,
    week_number: int,
    body: CreateLessonRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumResponse:

    dto: CreateLessonCommand = body.to_dto(
        curriculum_id=curriculum_id, owner_id=current_user.id, week_number=week_number
    )
    updated: CurriculumDTO = await curriculum_service.create_lesson(
        dto, RoleVO(current_user.role)
    )
    return CurriculumResponse.from_dto(updated)


@lesson_router.put(
    "/{curriculum_id}/weeks/{week_number}/lessons/{lesson_index}",
    response_model=CurriculumResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_lesson(
    curriculum_id: str,
    week_number: int,
    lesson_index: int,
    body: UpdateLessonRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> CurriculumResponse:

    dto: UpdateLessonCommand = body.to_dto(
        curriculum_id=curriculum_id,
        owner_id=current_user.id,
        week_number=week_number,
        lesson_index=lesson_index,
    )
    updated: CurriculumDTO = await curriculum_service.update_lesson(
        dto, RoleVO(current_user.role)
    )
    return CurriculumResponse.from_dto(updated)


@lesson_router.delete(
    "/{curriculum_id}/weeks/{week_number}/lessons/{lesson_index}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_lesson(
    curriculum_id: str,
    week_number: int,
    lesson_index: int,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    curriculum_service: CurriculumService = Depends(
        Provide[Container.curriculum_service]
    ),
) -> None:

    dto: DeleteLessonCommand = DeleteLessonCommand(
        curriculum_id=curriculum_id,
        owner_id=current_user.id,
        week_number=week_number,
        lesson_index=lesson_index,
    )

    await curriculum_service.delete_lesson(dto, RoleVO(current_user.role))
