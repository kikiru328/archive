from datetime import datetime, timezone
from ulid import ULID  # type: ignore
from app.common.monitoring.metrics import increment_summary_creation
from app.modules.learning.application.dto.learning_dto import (
    CreateSummaryCommand,
    UpdateSummaryCommand,
    SummaryDTO,
    SummaryPageDTO,
    SummaryQuery,
)
from app.modules.learning.application.exception import (
    SummaryNotFoundError,
    SummaryAccessDeniedError,
)
from app.modules.learning.domain.entity.summary import Summary
from app.modules.learning.domain.repository.summary_repo import ISummaryRepository
from app.modules.learning.domain.service.learning_domain_service import (
    LearningDomainService,
)
from app.modules.learning.domain.vo.summary_content import SummaryContent
from app.modules.user.domain.vo.role import RoleVO


class SummaryService:
    def __init__(
        self,
        summary_repo: ISummaryRepository,
        learning_domain_service: LearningDomainService,
        ulid: ULID = ULID(),
    ) -> None:
        self.summary_repo: ISummaryRepository = summary_repo
        self.learning_domain_service: LearningDomainService = learning_domain_service
        self.ulid: ULID = ulid

    async def create_summary(
        self,
        command: CreateSummaryCommand,
        role: RoleVO,
    ) -> SummaryDTO:
        """요약 생성"""
        # 커리큘럼에 해당 주차가 존재하는지 확인
        week_exists: bool = (
            await self.learning_domain_service.validate_week_exists_in_curriculum(
                curriculum_id=command.curriculum_id,
                week_number=command.week_number,
                user_id=command.owner_id,
                role=role,
            )
        )

        if not week_exists:
            raise SummaryNotFoundError(
                f"Week {command.week_number} not found in curriculum {command.curriculum_id}"
            )

        summary: Summary = await self.learning_domain_service.create_summary(
            summary_id=self.ulid.generate(),
            curriculum_id=command.curriculum_id,
            week_number=command.week_number,
            content=command.content,
            owner_id=command.owner_id,
        )

        await self.summary_repo.save(summary)
        increment_summary_creation()
        return SummaryDTO.from_domain(summary)

    async def get_summary_by_id(
        self,
        summary_id: str,
        user_id: str,
        role: RoleVO,
    ) -> SummaryDTO:
        """ID로 요약 조회"""
        summary: Summary | None = await self.summary_repo.find_by_id(summary_id)
        if not summary:
            raise SummaryNotFoundError(f"Summary {summary_id} not found")

        # 접근 권한 확인
        can_access: bool = await self.learning_domain_service.can_access_summary(
            summary=summary,
            owner_id=user_id,
            role=role,
        )

        if not can_access:
            raise SummaryAccessDeniedError("Access denied to summary")

        return SummaryDTO.from_domain(summary)

    async def get_summaries(
        self,
        query: SummaryQuery,
        user_id: str,
        role: RoleVO,
    ) -> SummaryPageDTO:
        """요약 목록 조회"""
        if query.curriculum_id and query.week_number:
            # 특정 커리큘럼의 특정 주차 요약들
            total_count, summaries = (
                await self.summary_repo.find_by_curriculum_and_week(
                    curriculum_id=query.curriculum_id,
                    week_number=query.week_number,
                    page=query.page,
                    items_per_page=query.items_per_page,
                )
            )
        elif query.curriculum_id:
            # 특정 커리큘럼의 모든 요약들
            total_count, summaries = await self.summary_repo.find_by_curriculum(
                curriculum_id=query.curriculum_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        elif query.owner_id or role != RoleVO.ADMIN:
            # 사용자의 모든 요약들 (일반 사용자는 자신의 것만)
            owner_id = query.owner_id or user_id
            total_count, summaries = await self.summary_repo.find_by_user(
                owner_id=owner_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        else:
            # 관리자의 경우 모든 요약 조회 (구현 필요시)
            total_count, summaries = await self.summary_repo.find_by_user(
                owner_id=user_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )

        # 접근 권한 필터링
        accessible_summaries = []
        for summary in summaries:
            can_access: bool = await self.learning_domain_service.can_access_summary(
                summary=summary,
                owner_id=user_id,
                role=role,
            )
            if can_access:
                accessible_summaries.append(summary)

        return SummaryPageDTO.from_domain(
            total_count=len(accessible_summaries),
            page=query.page,
            items_per_page=query.items_per_page,
            summaries=accessible_summaries,
        )

    async def update_summary(
        self,
        command: UpdateSummaryCommand,
        role: RoleVO,
    ) -> SummaryDTO:
        """요약 수정"""
        summary: Summary | None = await self.summary_repo.find_by_id(command.summary_id)
        if not summary:
            raise SummaryNotFoundError(f"Summary {command.summary_id} not found")

        # 수정 권한 확인
        can_modify: bool = await self.learning_domain_service.can_modify_summary(
            summary=summary,
            user_id=command.owner_id,
            role=role,
        )

        if not can_modify:
            raise SummaryAccessDeniedError("Access denied to modify summary")

        summary.update_content(SummaryContent(command.content))
        summary.updated_at = datetime.now(timezone.utc)

        await self.summary_repo.update(summary)
        return SummaryDTO.from_domain(summary)

    async def delete_summary(
        self,
        summary_id: str,
        user_id: str,
        role: RoleVO,
    ) -> None:
        """요약 삭제"""
        summary: Summary | None = await self.summary_repo.find_by_id(summary_id)
        if not summary:
            raise SummaryNotFoundError(f"Summary {summary_id} not found")

        # 삭제 권한 확인
        can_modify: bool = await self.learning_domain_service.can_modify_summary(
            summary=summary,
            user_id=user_id,
            role=role,
        )

        if not can_modify:
            raise SummaryAccessDeniedError("Access denied to delete summary")

        await self.summary_repo.delete(summary_id)
