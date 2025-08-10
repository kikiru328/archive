from typing import Annotated
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.core.auth import CurrentUser, get_current_user
from app.core.di_container import Container
from app.modules.learning.application.service.learning_stats_service import (
    LearningStatsService,
)
from app.modules.learning.application.dto.learning_stats_dto import (
    UserLearningStatsQuery,
    UserLearningStatsDTO,
)
from app.modules.learning.interface.schema.learning_stats_schema import (
    UserLearningStatsResponse,
)
from app.modules.user.domain.vo.role import RoleVO


learning_stats_router = APIRouter(prefix="/users/me/learning", tags=["Learning Stats"])


@learning_stats_router.get("/stats", response_model=UserLearningStatsResponse)
@inject
async def get_my_learning_stats(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    days: int = Query(30, ge=7, le=365, description="통계 기간 (일수)"),
    learning_stats_service: LearningStatsService = Depends(
        Provide[Container.learning_stats_service]
    ),
) -> UserLearningStatsResponse:
    """내 학습 통계 조회"""

    query = UserLearningStatsQuery(
        user_id=current_user.id,
        days_ago=days,
    )

    stats_dto: UserLearningStatsDTO = (
        await learning_stats_service.get_user_learning_stats(
            query=query,
            role=RoleVO(current_user.role.value),
        )
    )

    return UserLearningStatsResponse.from_dto(stats_dto)


@learning_stats_router.get("/overview", response_model=dict)
@inject
async def get_learning_overview(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    learning_stats_service: LearningStatsService = Depends(
        Provide[Container.learning_stats_service]
    ),
) -> dict:
    """학습 현황 간단 요약 (대시보드용)"""

    query = UserLearningStatsQuery(
        user_id=current_user.id,
        days_ago=7,  # 최근 1주일
    )

    stats: UserLearningStatsDTO = await learning_stats_service.get_user_learning_stats(
        query=query,
        role=RoleVO(current_user.role.value),
    )

    # 간단한 요약 정보만 반환
    return {
        "total_summaries": stats.total_summaries,
        "total_feedbacks": stats.total_feedbacks,
        "active_curriculums": stats.active_curriculums,
        "current_streak": stats.learning_streak.current_streak,
        "average_score": stats.score_distribution.average_score,
        "weekly_goal_achievement": stats.weekly_goal_achievement,
        "recent_activities_count": len(stats.recent_activities),
    }


@learning_stats_router.get("/progress", response_model=dict)
@inject
async def get_curriculum_progress(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    learning_stats_service: LearningStatsService = Depends(
        Provide[Container.learning_stats_service]
    ),
) -> dict:
    """커리큘럼별 진도 현황"""

    query = UserLearningStatsQuery(
        user_id=current_user.id,
        days_ago=90,  # 최근 3개월
    )

    stats: UserLearningStatsDTO = await learning_stats_service.get_user_learning_stats(
        query=query,
        role=RoleVO(current_user.role.value),
    )

    return {
        "curriculum_progress": [
            {
                "curriculum_id": cp.curriculum_id,
                "title": cp.curriculum_title,
                "completion_rate": cp.completion_rate,
                "feedback_rate": cp.feedback_rate,
                "average_score": cp.average_score,
                "latest_activity": cp.latest_activity,
            }
            for cp in stats.curriculum_progress
        ],
        "completed_curriculums": stats.completed_curriculums,
        "active_curriculums": stats.active_curriculums,
    }


@learning_stats_router.get("/streak", response_model=dict)
@inject
async def get_learning_streak(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    learning_stats_service: LearningStatsService = Depends(
        Provide[Container.learning_stats_service]
    ),
) -> dict:
    """학습 연속성 정보"""

    query = UserLearningStatsQuery(
        user_id=current_user.id,
        days_ago=365,  # 1년
    )

    stats: UserLearningStatsDTO = await learning_stats_service.get_user_learning_stats(
        query=query,
        role=RoleVO(current_user.role.value),
    )

    return {
        "current_streak": stats.learning_streak.current_streak,
        "longest_streak": stats.learning_streak.longest_streak,
        "total_learning_days": stats.learning_streak.total_learning_days,
        "weekly_goal_achievement": stats.weekly_goal_achievement,
    }
