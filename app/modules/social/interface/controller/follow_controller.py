from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.social.application.exception import (
    AlreadyFollowingError,
    NotFollowingError,
    SelfFollowError,
    UserNotFoundError,
)
from app.modules.social.application.service.follow_service import FollowService
from app.modules.social.application.dto.follow_dto import FollowQuery
from app.modules.social.interface.schema.follow_schema import (
    FollowUserRequest,
    UnfollowUserRequest,
    FollowResponse,
    FollowersResponse,
    FolloweesResponse,
    FollowStatsResponse,
    FollowStatusResponse,
    FollowSuggestionsResponse,
)


follow_router = APIRouter(prefix="/social", tags=["Social - Follow"])


@follow_router.post(
    "/follow", response_model=FollowResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def follow_user(
    request: FollowUserRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FollowResponse:
    """사용자 팔로우"""
    try:
        command = request.to_command(current_user.id)
        dto = await follow_service.follow_user(command)
        return FollowResponse.from_dto(dto)
    except SelfFollowError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AlreadyFollowingError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@follow_router.delete("/unfollow", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def unfollow_user(
    request: UnfollowUserRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> None:
    """사용자 언팔로우"""
    try:
        command = request.to_command(current_user.id)
        await follow_service.unfollow_user(command)
    except NotFollowingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@follow_router.get("/users/{user_id}/followers", response_model=FollowersResponse)
@inject
async def get_user_followers(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FollowersResponse:
    """특정 사용자의 팔로워 목록 조회"""
    query = FollowQuery(
        user_id=user_id,
        page=page,
        items_per_page=items_per_page,
    )
    page_dto = await follow_service.get_followers(query, current_user.id)
    return FollowersResponse.from_dto(page_dto)


@follow_router.get("/users/{user_id}/following", response_model=FolloweesResponse)
@inject
async def get_user_following(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FolloweesResponse:
    """특정 사용자가 팔로우하는 사람들 목록 조회"""
    query = FollowQuery(
        user_id=user_id,
        page=page,
        items_per_page=items_per_page,
    )
    page_dto = await follow_service.get_followees(query, current_user.id)
    return FolloweesResponse.from_dto(page_dto)


@follow_router.get("/me/followers", response_model=FollowersResponse)
@inject
async def get_my_followers(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FollowersResponse:
    """내 팔로워 목록 조회"""
    query = FollowQuery(
        user_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )
    page_dto = await follow_service.get_followers(query, current_user.id)
    return FollowersResponse.from_dto(page_dto)


@follow_router.get("/me/following", response_model=FolloweesResponse)
@inject
async def get_my_following(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="페이지 번호"),
    items_per_page: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FolloweesResponse:
    """내가 팔로우하는 사람들 목록 조회"""
    query = FollowQuery(
        user_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )
    page_dto = await follow_service.get_followees(query, current_user.id)
    return FolloweesResponse.from_dto(page_dto)


@follow_router.get("/users/{user_id}/stats", response_model=FollowStatsResponse)
@inject
async def get_user_follow_stats(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FollowStatsResponse:
    """특정 사용자의 팔로우 통계 조회"""
    dto = await follow_service.get_follow_stats(user_id)
    return FollowStatsResponse.from_dto(dto)


@follow_router.get("/users/{user_id}/status", response_model=FollowStatusResponse)
@inject
async def get_follow_status(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FollowStatusResponse:
    """특정 사용자와의 팔로우 상태 확인"""
    status_info = await follow_service.check_follow_status(current_user.id, user_id)
    return FollowStatusResponse(
        is_following=status_info["is_following"],
        is_mutual=status_info["is_mutual"],
    )


@follow_router.get("/suggestions", response_model=FollowSuggestionsResponse)
@inject
async def get_follow_suggestions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=20, description="추천 사용자 수"),
    follow_service: FollowService = Depends(Provide[Container.follow_service]),
) -> FollowSuggestionsResponse:
    """팔로우 추천 사용자 목록 조회"""
    dto = await follow_service.get_follow_suggestions(current_user.id, limit)
    return FollowSuggestionsResponse.from_dto(dto)
