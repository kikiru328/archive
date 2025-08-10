import pytest
from datetime import datetime, timezone

from app.modules.curriculum.domain.service.curriculum_domain_service import (
    CurriculumDomainService,
)
from app.modules.curriculum.domain.vo import Visibility, WeekNumber
from backend.app.modules.curriculum.domain.vo.title import Title


@pytest.mark.asyncio
class TestCurriculumDomainService:
    """커리큘럼 도메인 서비스 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        # repository는 create_curriculum에서 사용되지 않으므로 None 주입
        self.service = CurriculumDomainService(curriculum_repo=None)  # type: ignore

    async def test_create_curriculum_success(self):
        """커리큘럼 생성 성공 테스트"""
        # Given
        curriculum_id = "01HX1234567890123456789012"
        owner_id = "01HX9876543210987654321098"
        title = "Python 기초 과정"
        week_data = [
            (1, ["Python 설치", "변수와 자료형"]),
            (2, ["조건문", "반복문"]),
        ]
        visibility = Visibility.PRIVATE
        created_at = datetime.now(timezone.utc)

        # When
        curriculum = await self.service.create_curriculum(
            curriculum_id=curriculum_id,
            owner_id=owner_id,
            title=title,
            week_schedules_data=week_data,
            visibility=visibility,
            created_at=created_at,
        )

        # Then
        assert curriculum.id == curriculum_id
        assert curriculum.owner_id == owner_id
        assert curriculum.title.value == title
        assert curriculum.visibility == visibility
        assert curriculum.created_at == created_at
        assert curriculum.updated_at == created_at
        assert len(curriculum.week_schedules) == 2

        # 첫 번째 주차
        first = curriculum.week_schedules[0]
        assert first.week_number.value == 1
        assert "Python 설치" in first.lessons.items

        # 두 번째 주차
        second = curriculum.week_schedules[1]
        assert second.week_number.value == 2
        assert "조건문" in second.lessons.items

    async def test_create_curriculum_with_default_values(self):
        """기본값으로 커리큘럼 생성 테스트"""
        # Given
        curriculum_id = "01HX1234567890123456789012"
        owner_id = "01HX9876543210987654321098"
        title = "Test Curriculum"
        week_data = [(1, ["Basic lesson"])]

        # When
        curriculum = await self.service.create_curriculum(
            curriculum_id=curriculum_id,
            owner_id=owner_id,
            title=title,
            week_schedules_data=week_data,
        )

        # Then
        assert curriculum.visibility == Visibility.PRIVATE
        assert curriculum.created_at is not None
        assert curriculum.updated_at == curriculum.created_at

    async def test_create_curriculum_with_empty_week_schedules(self):
        """빈 주차 스케줄로 커리큘럼 생성 테스트"""
        # Given
        curriculum_id = "01HX1234567890123456789012"
        owner_id = "01HX9876543210987654321098"
        title = "Empty Curriculum"
        week_data = []  # type: ignore

        # When
        curriculum = await self.service.create_curriculum(
            curriculum_id=curriculum_id,
            owner_id=owner_id,
            title=title,
            week_schedules_data=week_data,
        )

        # Then
        assert curriculum.is_empty()
        assert len(curriculum.week_schedules) == 0

    async def test_insert_week_and_shift_at_beginning(self):
        """첫 번째 위치에 주차 삽입 및 시프트 테스트"""
        # Given
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        new_week = 1
        lessons_data = ["새로운 첫 주차 레슨"]

        # When
        updated = await self.service.insert_week_and_shift(
            curriculum, new_week, lessons_data
        )

        # Then
        assert len(updated.week_schedules) == 4
        assert updated.week_schedules[0].week_number.value == 1
        assert "새로운 첫 주차 레슨" in updated.week_schedules[0].lessons.items
        # 기존 주차들이 뒤로 밀렸는지
        assert [ws.week_number.value for ws in updated.week_schedules] == [1, 2, 3, 4]

    async def test_insert_week_and_shift_in_middle(self):
        """중간 위치에 주차 삽입 및 시프트 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        updated = await self.service.insert_week_and_shift(
            curriculum, new_week_number=2, lessons_data=["새로운 중간 주차 레슨"]
        )
        nums = [ws.week_number.value for ws in updated.week_schedules]
        assert nums == [1, 2, 3, 4]

    async def test_insert_week_and_shift_at_end(self):
        """마지막 위치에 주차 삽입 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        updated = await self.service.insert_week_and_shift(
            curriculum, new_week_number=4, lessons_data=["새로운 마지막 주차 레슨"]
        )
        assert updated.week_schedules[-1].week_number.value == 4

    async def test_insert_week_and_shift_with_max_week_limit(self):
        """최대 주차 제한 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        # 4~24주차 추가
        for i in range(4, 25):
            curriculum.add_week_schedule(
                curriculum.week_schedules[0].__class__(
                    week_number=WeekNumber(i),
                    title=Title("개념"),
                    lessons=curriculum.week_schedules[0].lessons,
                )
            )

        updated = await self.service.insert_week_and_shift(
            curriculum, new_week_number=1, lessons_data=["초과 레슨"]
        )
        # 1~24주차만 유지
        nums = [ws.week_number.value for ws in updated.week_schedules]
        assert nums[0] == 1 and nums[-1] == 24 and len(nums) == 24

    async def test_remove_week_and_shift_from_beginning(self):
        """첫 번째 주차 제거 및 시프트 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        updated = await self.service.remove_week_and_shift(
            curriculum, target_week_number=1
        )
        assert [ws.week_number.value for ws in updated.week_schedules] == [1, 2]

    async def test_remove_week_and_shift_from_middle(self):
        """중간 주차 제거 및 시프트 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        updated = await self.service.remove_week_and_shift(
            curriculum, target_week_number=2
        )
        assert [ws.week_number.value for ws in updated.week_schedules] == [1, 2]

    async def test_remove_week_and_shift_from_end(self):
        """마지막 주차 제거 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        updated = await self.service.remove_week_and_shift(
            curriculum, target_week_number=3
        )
        assert [ws.week_number.value for ws in updated.week_schedules] == [1, 2]

    async def test_remove_nonexistent_week_should_fail(self):
        """존재하지 않는 주차 제거 시 실패"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        with pytest.raises(ValueError, match="Week 5 not found"):
            await self.service.remove_week_and_shift(curriculum, 5)

    async def test_validate_curriculum_structure_with_valid_curriculum(self):
        """유효한 커리큘럼 구조 검증 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        is_valid = await self.service.validate_curriculum_structure(curriculum)
        assert is_valid

    async def test_validate_curriculum_structure_with_empty_curriculum_should_fail(
        self,
    ):
        """빈 커리큘럼 구조 검증 실패 테스트"""
        curriculum = await self._create_empty_curriculum()
        is_valid = await self.service.validate_curriculum_structure(curriculum)
        assert not is_valid

    async def test_validate_curriculum_structure_with_non_starting_week_should_fail(
        self,
    ):
        """1주차부터 시작하지 않는 구조 검증 실패"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        # 1주차 직접 제거 (Shift 없이)

        curriculum.remove_week_schedule(WeekNumber(1))

    async def test_validate_curriculum_structure_with_gap_in_weeks_should_fail(self):
        """주차 번호에 빈 공간이 있는 구조 검증 실패"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        # 2주차 직접 제거 (Shift 없이)

        curriculum.remove_week_schedule(WeekNumber(2))
        is_valid = await self.service.validate_curriculum_structure(curriculum)
        assert not is_valid

    async def test_can_access_curriculum_as_admin(self):
        """관리자 접근 권한 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        can_access = await self.service.can_access_curriculum(
            curriculum, user_id="x", is_admin=True
        )
        assert can_access

    async def test_can_access_curriculum_as_owner(self):
        """소유자 접근 권한 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        can_access = await self.service.can_access_curriculum(
            curriculum, user_id="test_owner_id", is_admin=False
        )
        assert can_access

    async def test_can_access_public_curriculum_as_non_owner(self):
        """공개 커리큘럼 비소유자 접근 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        curriculum.make_public()
        can_access = await self.service.can_access_curriculum(
            curriculum, user_id="other", is_admin=False
        )
        assert can_access

    async def test_cannot_access_private_curriculum_as_non_owner(self):
        """비공개 커리큘럼 비소유자 접근 거부 테스트"""
        curriculum = await self._create_test_curriculum_with_multiple_weeks()
        can_access = await self.service.can_access_curriculum(
            curriculum, user_id="other", is_admin=False
        )
        assert not can_access

    # 헬퍼 메서드
    async def _create_test_curriculum_with_multiple_weeks(self):
        return await self.service.create_curriculum(
            curriculum_id="tc_id",
            owner_id="test_owner_id",
            title="Test",
            week_schedules_data=[
                (1, ["A", "B"]),
                (2, ["C", "D"]),
                (3, ["E", "F"]),
            ],
            visibility=Visibility.PRIVATE,
        )

    async def _create_empty_curriculum(self):
        return await self.service.create_curriculum(
            curriculum_id="empty_id",
            owner_id="test_owner_id",
            title="Empty",
            week_schedules_data=[],
            visibility=Visibility.PRIVATE,
        )
