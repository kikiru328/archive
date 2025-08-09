from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.learning.application.service.feedback_service import FeedbackService
from app.modules.learning.application.dto.learning_dto import (
    FeedbackQuery,
    FeedbackDTO,
    FeedbackPageDTO,
)
from app.modules.learning.interface.schema.feedback_schema import (
    FeedbackResponse,
    FeedbackPageResponse,
    GenerateFeedbackRequest,
)
from app.modules.user.domain.vo.role import RoleVO


feedback_router = APIRouter(prefix="/summaries", tags=["Feedbacks"])


# @feedback_router.post(
#     "/{summary_id}/feedbacks",
#     response_model=FeedbackResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# @inject
# async def create_feedback(
#     summary_id: str,
#     request: CreateFeedbackRequest,
#     current_user: Annotated[CurrentUser, Depends(get_current_user)],
#     feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
# ) -> FeedbackResponse:
#     """피드백 생성 (수동)"""
#     command: CreateFeedbackCommand = request.to_command(
#         summary_id=summary_id,
#         owner_id=current_user.id,
#     )

#     dto: FeedbackDTO = await feedback_service.create_feedback(
#         command=command,
#         role=RoleVO(current_user.role.value),
#     )

#     return FeedbackResponse.from_dto(dto)


@feedback_router.post(
    "/{summary_id}/feedbacks/generate",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def generate_feedback_with_ai(
    summary_id: str,
    request: GenerateFeedbackRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
) -> FeedbackResponse:
    """AI 피드백 생성 (자동)"""
    dto: FeedbackDTO = await feedback_service.generate_feedback_with_llm(
        summary_id=summary_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return FeedbackResponse.from_dto(dto)


@feedback_router.get(
    "/{summary_id}/feedbacks",
    response_model=Optional[FeedbackResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get_feedback_by_summary(
    summary_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
) -> Optional[FeedbackResponse]:
    """요약의 피드백 조회"""
    dto: Optional[FeedbackDTO] = await feedback_service.get_feedback_by_summary_id(
        summary_id=summary_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    if not dto:
        return None

    return FeedbackResponse.from_dto(dto)


@feedback_router.get(
    "/feedbacks/{feedback_id}",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_feedback_by_id(
    feedback_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
) -> FeedbackResponse:
    """ID로 피드백 상세 조회"""
    dto: FeedbackDTO = await feedback_service.get_feedback_by_id(
        feedback_id=feedback_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return FeedbackResponse.from_dto(dto)


# @feedback_router.put(
#     "/feedbacks/{feedback_id}",
#     response_model=FeedbackResponse,
#     status_code=status.HTTP_200_OK,
# )
# @inject
# async def update_feedback(
#     feedback_id: str,
#     request: UpdateFeedbackRequest,
#     current_user: Annotated[CurrentUser, Depends(get_current_user)],
#     feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
# ) -> FeedbackResponse:
#     """피드백 수정"""
#     command: UpdateFeedbackCommand = request.to_command(
#         feedback_id=feedback_id,
#         owner_id=current_user.id,
#     )

#     dto: FeedbackDTO = await feedback_service.update_feedback(
#         command=command,
#         role=RoleVO(current_user.role.value),
#     )

#     return FeedbackResponse.from_dto(dto)


@feedback_router.delete(
    "/feedbacks/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_feedback(
    feedback_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
) -> None:
    """피드백 삭제"""
    await feedback_service.delete_feedback(
        feedback_id=feedback_id,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )


# 커리큘럼별 피드백 조회
curriculum_feedback_router = APIRouter(
    prefix="/curriculums", tags=["Curriculum Feedbacks"]
)


@curriculum_feedback_router.get(
    "/{curriculum_id}/feedbacks",
    response_model=FeedbackPageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_feedbacks_by_curriculum(
    curriculum_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
) -> FeedbackPageResponse:
    """특정 커리큘럼의 모든 피드백 목록 조회"""
    query = FeedbackQuery(
        curriculum_id=curriculum_id,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: FeedbackPageDTO = await feedback_service.get_feedbacks(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return FeedbackPageResponse.from_dto(page_dto)


# 사용자별 피드백 관련 엔드포인트
user_feedback_router = APIRouter(prefix="/users/me/feedbacks", tags=["Users"])


@user_feedback_router.get(
    "", response_model=FeedbackPageResponse, status_code=status.HTTP_200_OK
)
@inject
async def get_my_feedbacks(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    min_score: Optional[float] = Query(None, ge=0.0, le=10.0, description="최소 점수"),
    max_score: Optional[float] = Query(None, ge=0.0, le=10.0, description="최대 점수"),
    feedback_service: FeedbackService = Depends(Provide[Container.feedback_service]),
) -> FeedbackPageResponse:
    """내가 받은 모든 피드백 목록 조회"""
    query = FeedbackQuery(
        owner_id=current_user.id,
        min_score=min_score,
        max_score=max_score,
        page=page,
        items_per_page=items_per_page,
    )

    page_dto: FeedbackPageDTO = await feedback_service.get_feedbacks(
        query=query,
        user_id=current_user.id,
        role=RoleVO(current_user.role.value),
    )

    return FeedbackPageResponse.from_dto(page_dto)
