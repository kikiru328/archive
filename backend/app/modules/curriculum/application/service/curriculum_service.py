from datetime import datetime, timezone
from typing import Optional
from ulid import ULID  # type: ignore
from app.common.llm.llm_client_repo import ILLMClientRepository
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
from app.modules.curriculum.application.exception import (
    CurriculumCountOverError,
    CurriculumNotFoundError,
    LLMGenerationError,
    WeekIndexOutOfRangeError,
    WeekScheduleNotFoundError,
    InvalidLLMResponseError,
)
from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.curriculum.domain.service.curriculum_domain_service import (
    CurriculumDomainService,
)
from app.modules.curriculum.domain.vo.lessons import Lessons
from app.modules.curriculum.domain.vo.title import Title
from app.modules.curriculum.domain.vo.visibility import Visibility
from app.modules.curriculum.domain.vo.week_number import WeekNumber
from app.modules.user.domain.vo.role import RoleVO
from app.modules.social.domain.repository.follow_repo import IFollowRepository
from app.common.monitoring.metrics import increment_curriculum_creation
from app.common.llm.decorators import trace_llm_operation


class CurriculumService:
    def __init__(
        self,
        curriculum_repo: ICurriculumRepository,
        curriculum_domain_service: CurriculumDomainService,
        llm_client: ILLMClientRepository,
        follow_repo: IFollowRepository,  # 추가
        ulid: ULID = ULID(),
        # feed_event_handler: Optional[CurriculumEventHandler] = None,
    ) -> None:

        self.curriculum_repo: ICurriculumRepository = curriculum_repo
        self.curriculum_domain_service: CurriculumDomainService = (
            curriculum_domain_service
        )
        self.llm_client: ILLMClientRepository = llm_client
        self.ulid: ULID = ulid
        self.follow_repo: IFollowRepository = follow_repo  # 추가
        # self.feed_event_handler = feed_event_handler  # 추가

    def _parse_llm_response(self, llm_response: dict, goal: str) -> dict:  # type: ignore
        try:
            # LLM 응답 구조 확인 및 파싱
            if isinstance(llm_response, dict):  # type: ignore
                title_str = llm_response.get("title", "")  # type: ignore
                schedule_list = llm_response.get("schedule", [])  # type: ignore

            elif isinstance(llm_response, list):  # type: ignore
                # 배열 형태의 응답 처리
                first_item = llm_response[0] if llm_response else {}
                if isinstance(first_item, dict) and "schedule" in first_item:
                    title_str = first_item.get("title", "") or goal
                    schedule_list = first_item.get("schedule", [])
                else:
                    # 스케줄 배열 자체인 경우
                    title_str = goal
                    schedule_list = llm_response
            else:
                raise InvalidLLMResponseError("Invalid LLM response format")

            # 제목에 타임스탬프 추가
            now: datetime = datetime.now(timezone.utc)
            prefix = now.strftime("%y%m%d%H%M")
            full_title = f"{prefix} {title_str}" if title_str else f"{prefix} {goal}"

            # 스케줄 데이터 변환 및 검증
            week_schedules = []
            for item in schedule_list:  # type: ignore
                if not isinstance(item, dict):
                    continue

                # 주차 번호 추출 (여러 키 형태 지원)
                week_num = (  # type: ignore
                    item.get("week_number")  # type: ignore
                    or item.get("weekNumber")  # type: ignore
                    or item.get("week")  # type: ignore
                )

                # 주차 제목(여러 키 형태 지원)
                week_title_raw = (
                    item.get("title")  # type: ignore
                    or item.get("week_title")  # type: ignore
                    or None
                )

                # 레슨 리스트 추출 (여러 키 형태 지원)
                lessons_raw = (  # type: ignore
                    item.get("lessons")  # type: ignore
                    or item.get("topics")  # type: ignore
                    or item.get("content")  # type: ignore
                    or []
                )

                if week_num is None or not lessons_raw:
                    continue

                # 유효성 검증
                if not isinstance(week_num, int) or week_num < 1:
                    continue

                if not isinstance(lessons_raw, list):
                    lessons_raw: list[str] = [str(lessons_raw)]  #  type: ignore

                # 빈 레슨 제거 및 문자열 변환
                lessons: list[str] = [str(lesson).strip() for lesson in lessons_raw if str(lesson).strip()]  # type: ignore

                if lessons:
                    # 1) LLM이 접두사를 붙였으면 제거: "1주차: ", "3 주차 -", 등
                    def _strip_prefix(s: str, n: int) -> str:
                        import re

                        s = s.strip()
                        # 숫자/주차/구분자(:：- ) 제거
                        s = re.sub(rf"^\s*{n}\s*주차\s*[:：\-]?\s*", "", s)
                        return s.strip()

                    # 2) 없거나 너무 짧으면 첫 레슨으로 보정
                    def _fallback_title(n: int, ls: list[str]) -> str:
                        return ls[0][:50] if ls else str(goal)[:50]

                    week_title = str(week_title_raw).strip() if week_title_raw else ""
                    if week_title:
                        week_title = _strip_prefix(week_title, week_num)
                    if not week_title:
                        week_title = _fallback_title(week_num, lessons)

                    # (week, title, lessons)
                    week_schedules.append((week_num, week_title, lessons))  # type: ignore

            # 최소 1개 주차는 있어야 함
            if not week_schedules:
                raise ValueError("No valid week schedules found in LLM response")

            # 주차 번호 순으로 정렬
            week_schedules.sort(key=lambda x: x[0])  # type: ignore

            return {
                "title": full_title,
                "week_schedules": week_schedules,
            }  # type: ignore

        except Exception as e:
            raise LLMGenerationError(f"Failed to parse LLM response: {str(e)}")

    async def create_curriculum(
        self,
        command: CreateCurriculumCommand,
        created_at: Optional[datetime] = None,
    ) -> CurriculumDTO:

        count: int = await self.curriculum_repo.count_by_owner(command.owner_id)
        if count >= 10:
            raise CurriculumCountOverError(
                "You can only have to 10 curriculums. Delete one before creating a new one"
            )

        curriculum: Curriculum = await self.curriculum_domain_service.create_curriculum(
            curriculum_id=self.ulid.generate(),
            owner_id=command.owner_id,
            title=command.title,
            week_schedules_data=command.week_schedules,
            visibility=command.visibility,
            created_at=created_at,
        )

        await self.curriculum_repo.save(curriculum)

        increment_curriculum_creation()

        return CurriculumDTO.from_domain(curriculum)

    @trace_llm_operation("generate_curriculum")
    async def generate_curriculum(
        self,
        command: GenerateCurriculumCommand,
    ) -> CurriculumDTO:
        print(f"🔥🔥🔥 LLM Client Type: {type(self.llm_client).__name__}")
        print(f"🔥🔥🔥 LLM Client Module: {type(self.llm_client).__module__}")

        count: int = await self.curriculum_repo.count_by_owner(command.owner_id)
        if count >= 10:
            raise CurriculumCountOverError(
                "You can only have to 10 curriculums. Delete one before creating a new one"
            )

        try:
            llm_response = await self.llm_client.generate_curriculum(
                goal=command.goal,
                period=command.period,
                difficulty=command.difficulty,
                details=command.details,
            )

            curriculum_data = self._parse_llm_response(  # type: ignore
                llm_response=llm_response,
                goal=command.goal,
            )

        except Exception as e:
            raise LLMGenerationError(f"Failed to generate curriculum: {str(e)}")

        curriculum: Curriculum = await self.curriculum_domain_service.create_curriculum(
            curriculum_id=self.ulid.generate(),
            owner_id=command.owner_id,
            title=curriculum_data["title"],
            week_schedules_data=curriculum_data["week_schedules"],
            visibility=Visibility.PRIVATE,
        )

        await self.curriculum_repo.save(curriculum)
        increment_curriculum_creation()
        return CurriculumDTO.from_domain(curriculum)

    async def get_curriculums(
        self,
        query: CurriculumQuery,
        # role: RoleVO,
    ) -> CurriculumPageDTO:

        if query.owner_id:
            total_count, curriculums = await self.curriculum_repo.find_by_owner_id(
                owner_id=query.owner_id,
                page=query.page,
                items_per_page=query.items_per_page,
            )
        else:
            total_count, curriculums = (
                await self.curriculum_repo.find_public_curriculums(
                    page=query.page,
                    items_per_page=query.items_per_page,
                )
            )

        return CurriculumPageDTO.from_domain(
            total_count=total_count,
            page=query.page,
            items_per_page=query.items_per_page,
            curriculums=curriculums,
        )

    async def get_curriculum_by_id(
        self,
        curriculum_id: str,
        role: RoleVO,
        owner_id: Optional[str] = None,
    ) -> CurriculumDTO:
        curriculum = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(f"Curriculum {curriculum_id} not found")

        return CurriculumDTO.from_domain(curriculum)

    async def update_curriculum(
        self,
        command: UpdateCurriculumCommand,
        role: RoleVO,
    ) -> CurriculumDTO:

        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=command.owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        if role != RoleVO.ADMIN and curriculum.owner_id != command.owner_id:
            raise PermissionError("You can only update your own curriculum")

        # visibility_changed = (
        #     command.visibility and curriculum.visibility != command.visibility
        # )

        # 업데이트
        if command.title:
            curriculum.change_title(Title(command.title))

        if command.visibility:
            curriculum.change_visibility(command.visibility)

        await self.curriculum_repo.update(curriculum)

        # if self.feed_event_handler:
        #     if visibility_changed:
        #         await self.feed_event_handler.on_curriculum_visibility_changed(curriculum.id)
        #     else:
        #         await self.feed_event_handler.on_curriculum_updated(curriculum.id)

        return CurriculumDTO.from_domain(curriculum)

    async def delete_curriculum(
        self,
        curriculum_id: str,
        owner_id: str,
        role: RoleVO,
    ) -> None:

        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(f"Curriculum {curriculum_id} not found")

        if role != RoleVO.ADMIN and curriculum.owner_id != owner_id:
            raise PermissionError("You can only delete your own curriculum")

        await self.curriculum_repo.delete(curriculum_id)

    async def create_week_schedule(
        self,
        command: CreateWeekScheduleCommand,
        role: RoleVO,
    ) -> CurriculumDTO:
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=command.owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        if role != RoleVO.ADMIN and curriculum.owner_id != command.owner_id:
            raise PermissionError("You can only modify your own curriculum")

        updated_curriculum = await self.curriculum_domain_service.insert_week_and_shift(
            curriculum=curriculum,
            new_week_number=command.week_number,
            lessons_data=command.lessons,
            new_week_title=command.title,
        )

        await self.curriculum_repo.update(updated_curriculum)
        return CurriculumDTO.from_domain(updated_curriculum)

    async def delete_week_schedule(
        self,
        curriculum_id: str,
        owner_id: str,
        week_number: int,
        role: RoleVO,
    ) -> None:
        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=curriculum_id,
            role=role,
            owner_id=owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(f"Curriculum {curriculum_id} not found")

        if role != RoleVO.ADMIN and curriculum.owner_id != owner_id:
            raise PermissionError("You can only modify your own curriculum")

        target_week = WeekNumber(week_number)
        if not curriculum.has_week(target_week):
            raise WeekScheduleNotFoundError(f"Week {week_number} not found")

        # 도메인 서비스를 통한 주차 제거
        updated_curriculum = await self.curriculum_domain_service.remove_week_and_shift(
            curriculum=curriculum,
            target_week_number=week_number,
        )

        await self.curriculum_repo.update(updated_curriculum)

    async def create_lesson(
        self,
        command: CreateLessonCommand,
        role: RoleVO,
    ) -> CurriculumDTO:

        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=command.owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        if role != RoleVO.ADMIN and curriculum.owner_id != command.owner_id:
            raise PermissionError("You can only modify your own curriculum")

        target_week = WeekNumber(command.week_number)
        week_schedule: WeekSchedule | None = curriculum.get_week_schedule(target_week)

        if not week_schedule:
            raise WeekScheduleNotFoundError(f"Week {command.week_number} not found")

        insert_index = (
            command.lesson_index
            if command.lesson_index is not None
            else week_schedule.lessons.count
        )

        if not (0 <= insert_index <= week_schedule.lessons.count):
            raise WeekIndexOutOfRangeError("Lesson index out of range")

        lessons_list = week_schedule.lessons.items
        lessons_list.insert(insert_index, command.lesson)

        updated_week_schedule = WeekSchedule(
            week_number=target_week,
            title=week_schedule.title,
            lessons=Lessons(lessons_list),
        )

        curriculum.update_week_schedule(target_week, updated_week_schedule)

        await self.curriculum_repo.update(curriculum)
        return CurriculumDTO.from_domain(curriculum)

    async def update_lesson(
        self,
        command: UpdateLessonCommand,
        role: RoleVO,
    ) -> CurriculumDTO:

        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=command.owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        if role != RoleVO.ADMIN and curriculum.owner_id != command.owner_id:
            raise PermissionError("You can only modify your own curriculum")

        target_week = WeekNumber(command.week_number)
        week_schedule: WeekSchedule | None = curriculum.get_week_schedule(target_week)

        if not week_schedule:
            raise WeekScheduleNotFoundError(f"Week {command.week_number} not found")

        if not (0 <= command.lesson_index < week_schedule.lessons.count):
            raise WeekIndexOutOfRangeError("Lesson index out of range")

        updated_week_schedule: WeekSchedule = week_schedule.update_lesson_at(
            index=command.lesson_index,
            new_lesson=command.new_lesson,
        )

        curriculum.update_week_schedule(target_week, updated_week_schedule)

        await self.curriculum_repo.update(curriculum)
        return CurriculumDTO.from_domain(curriculum)

    async def delete_lesson(
        self,
        command: DeleteLessonCommand,
        role: RoleVO,
    ) -> CurriculumDTO:

        curriculum: Curriculum | None = await self.curriculum_repo.find_by_id(
            curriculum_id=command.curriculum_id,
            role=role,
            owner_id=command.owner_id,
        )

        if not curriculum:
            raise CurriculumNotFoundError(
                f"Curriculum {command.curriculum_id} not found"
            )

        if role != RoleVO.ADMIN and curriculum.owner_id != command.owner_id:
            raise PermissionError("You can only modify your own curriculum")

        target_week = WeekNumber(command.week_number)
        week_schedule: WeekSchedule | None = curriculum.get_week_schedule(target_week)

        if not week_schedule:
            raise WeekScheduleNotFoundError(f"Week {command.week_number} not found")

        if not (0 <= command.lesson_index < week_schedule.lessons.count):
            raise WeekIndexOutOfRangeError("Lesson index out of range")

        updated_week_schedule: WeekSchedule = week_schedule.remove_lesson_at(
            command.lesson_index
        )

        curriculum.update_week_schedule(target_week, updated_week_schedule)

        await self.curriculum_repo.update(curriculum)
        return CurriculumDTO.from_domain(curriculum)

    async def get_following_users_curriculums(
        self,
        user_id: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> CurriculumPageDTO:
        """팔로우한 사용자들의 public 커리큘럼 목록 조회"""

        # 팔로우한 사용자들 조회
        _, follows = await self.follow_repo.find_followees(
            user_id, page=1, items_per_page=1000  # 모든 팔로잉 사용자 조회
        )

        if not follows:
            return CurriculumPageDTO.from_domain(
                total_count=0,
                page=page,
                items_per_page=items_per_page,
                curriculums=[],
            )

        followee_ids = [follow.followee_id for follow in follows]

        # 팔로우한 사용자들의 public 커리큘럼 조회
        total_count, curriculums = (
            await self.curriculum_repo.find_public_curriculums_by_users(
                user_ids=followee_ids,
                page=page,
                items_per_page=items_per_page,
            )
        )

        return CurriculumPageDTO.from_domain(
            total_count=total_count,
            page=page,
            items_per_page=items_per_page,
            curriculums=curriculums,
        )
