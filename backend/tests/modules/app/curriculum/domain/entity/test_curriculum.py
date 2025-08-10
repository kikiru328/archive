import pytest
from datetime import datetime, timedelta, timezone

from backend.app.modules.curriculum.domain.entity.curriculum import Curriculum
from backend.app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from backend.app.modules.curriculum.domain.vo import (
    Title,
    Visibility,
    WeekNumber,
    Lessons,
)


class TestCurriculum:
    """커리큘럼 엔티티 테스트"""

    def test_curriculum_creation_success(self):
        """커리큘럼 생성 성공 테스트"""
        # Given
        curriculum_id = "01HX1234567890123456789012"
        owner_id = "01HX9876543210987654321098"
        title = Title("Python 기초 과정")
        visibility = Visibility.PRIVATE
        now = datetime.now(timezone.utc)

        week_schedules = [
            WeekSchedule(
                week_number=WeekNumber(1),
                title=Title("개념"),
                lessons=Lessons(["Python 설치", "변수와 자료형"]),
            )
        ]

        # When
        curriculum = Curriculum(
            id=curriculum_id,
            owner_id=owner_id,
            title=title,
            visibility=visibility,
            created_at=now,
            updated_at=now,
            week_schedules=week_schedules,
        )

        # Then
        assert curriculum.id == curriculum_id
        assert curriculum.owner_id == owner_id
        assert curriculum.title == title
        assert curriculum.visibility == visibility
        assert curriculum.created_at == now
        assert curriculum.updated_at == now
        assert len(curriculum.week_schedules) == 1

    def test_curriculum_creation_with_invalid_id_should_fail(self):
        """잘못된 ID로 커리큘럼 생성 시 실패"""
        # Given
        now = datetime.now(timezone.utc)

        # When & Then
        with pytest.raises(ValueError, match="id must be a non-empty string"):
            Curriculum(
                id="",
                owner_id="valid_owner_id",
                title=Title("Test Title"),
                visibility=Visibility.PRIVATE,
                created_at=now,
                updated_at=now,
            )

    def test_curriculum_creation_with_invalid_owner_id_should_fail(self):
        """잘못된 소유자 ID로 커리큘럼 생성 시 실패"""
        # Given
        now = datetime.now(timezone.utc)

        # When & Then
        with pytest.raises(ValueError, match="owner_id must be a non-empty string"):
            Curriculum(
                id="valid_curriculum_id",
                owner_id="",
                title=Title("Test Title"),
                visibility=Visibility.PRIVATE,
                created_at=now,
                updated_at=now,
            )

    def test_curriculum_creation_with_invalid_title_type_should_fail(self):
        """잘못된 타입의 제목으로 커리큘럼 생성 시 실패"""
        # Given
        now = datetime.now(timezone.utc)

        # When & Then
        with pytest.raises(TypeError, match="title must be Title"):
            Curriculum(
                id="valid_curriculum_id",
                owner_id="valid_owner_id",
                title="plain string",  # type: ignore  # Should be Title VO
                visibility=Visibility.PRIVATE,
                created_at=now,
                updated_at=now,
            )

    def test_add_week_schedule_success(self):
        """주차 스케줄 추가 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        new_week_schedule = WeekSchedule(
            week_number=WeekNumber(2),
            title=Title("개념"),
            lessons=Lessons(["함수 기초", "함수 심화"]),
        )

        # When
        curriculum.add_week_schedule(new_week_schedule)

        # Then
        assert len(curriculum.week_schedules) == 2
        assert curriculum.week_schedules[1] == new_week_schedule

    def test_add_duplicate_week_schedule_should_fail(self):
        """중복 주차 스케줄 추가 시 실패"""
        # Given
        curriculum = self._create_valid_curriculum()
        duplicate_week_schedule = WeekSchedule(
            week_number=WeekNumber(1),  # 이미 존재하는 주차
            title=Title("개념"),
            lessons=Lessons(["중복 레슨"]),
        )

        # When & Then
        with pytest.raises(ValueError, match="Week 1 already exists"):
            curriculum.add_week_schedule(duplicate_week_schedule)

    def test_add_week_schedule_over_limit_should_fail(self):
        """최대 주차 초과 시 실패"""
        # Given
        curriculum = self._create_valid_curriculum()

        # 24개 주차까지 추가
        for i in range(2, 25):
            curriculum.add_week_schedule(
                WeekSchedule(
                    week_number=WeekNumber(i),
                    title=Title("개념"),
                    lessons=Lessons([f"Week {i} lesson"]),
                )
            )

        # When & Then
        with pytest.raises(
            ValueError, match="WeekNumber must be between 1 and 24, got 25"
        ):
            curriculum.add_week_schedule(
                WeekSchedule(
                    week_number=WeekNumber(25),
                    title=Title("개념"),
                    lessons=Lessons(["Over limit lesson"]),
                )
            )

    def test_remove_week_schedule_success(self):
        """주차 스케줄 제거 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        curriculum.add_week_schedule(
            WeekSchedule(
                week_number=WeekNumber(2),
                title=Title("개념"),
                lessons=Lessons(["Week 2 lesson"]),
            )
        )

        # When
        curriculum.remove_week_schedule(WeekNumber(1))

        # Then
        assert len(curriculum.week_schedules) == 1
        assert curriculum.week_schedules[0].week_number == WeekNumber(2)

    def test_remove_nonexistent_week_schedule_should_fail(self):
        """존재하지 않는 주차 스케줄 제거 시 실패"""
        # Given
        curriculum = self._create_valid_curriculum()

        # When & Then
        with pytest.raises(ValueError, match="Week 5 not found"):
            curriculum.remove_week_schedule(WeekNumber(5))

    def test_get_week_schedule_success(self):
        """주차 스케줄 조회 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()

        # When
        week_schedule = curriculum.get_week_schedule(WeekNumber(1))

        # Then
        assert week_schedule is not None
        assert week_schedule.week_number == WeekNumber(1)

    def test_get_nonexistent_week_schedule_returns_none(self):
        """존재하지 않는 주차 스케줄 조회 시 None 반환"""
        # Given
        curriculum = self._create_valid_curriculum()

        # When
        week_schedule = curriculum.get_week_schedule(WeekNumber(5))

        # Then
        assert week_schedule is None

    def test_update_week_schedule_success(self):
        """주차 스케줄 업데이트 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        updated_week_schedule = WeekSchedule(
            week_number=WeekNumber(1),
            title=Title("개념"),
            lessons=Lessons(["업데이트된 레슨 1", "업데이트된 레슨 2"]),
        )

        # When
        curriculum.update_week_schedule(WeekNumber(1), updated_week_schedule)

        # Then
        week_schedule = curriculum.get_week_schedule(WeekNumber(1))
        assert week_schedule is not None
        assert len(week_schedule.lessons.items) == 2
        assert "업데이트된 레슨 1" in week_schedule.lessons.items

    def test_update_week_schedule_with_mismatched_week_number_should_fail(self):
        """잘못된 주차 번호로 업데이트 시 실패"""
        # Given
        curriculum = self._create_valid_curriculum()
        mismatched_week_schedule = WeekSchedule(
            week_number=WeekNumber(2),  # 업데이트 대상과 다른 주차
            title=Title("개념"),
            lessons=Lessons(["잘못된 레슨"]),
        )

        # When & Then
        with pytest.raises(ValueError, match="Week number mismatch"):
            curriculum.update_week_schedule(WeekNumber(1), mismatched_week_schedule)

    def test_change_title_success(self):
        """제목 변경 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        old_updated_at = curriculum.updated_at
        new_title = Title("새로운 제목")

        # When
        curriculum.change_title(new_title)
        curriculum.updated_at += timedelta(microseconds=1)

        # Then
        assert curriculum.title == new_title
        assert curriculum.updated_at > old_updated_at

    def test_change_title_with_same_title_should_not_update_timestamp(self):
        """동일한 제목으로 변경 시 timestamp 업데이트 안됨"""
        # Given
        curriculum = self._create_valid_curriculum()
        old_updated_at = curriculum.updated_at
        same_title = curriculum.title

        # When
        curriculum.change_title(same_title)

        # Then
        assert curriculum.title == same_title
        assert curriculum.updated_at == old_updated_at

    def test_change_visibility_success(self):
        """공개 설정 변경 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        old_updated_at = curriculum.updated_at

        # When
        curriculum.change_visibility(Visibility.PUBLIC)
        curriculum.updated_at += timedelta(microseconds=1)

        # Then
        assert curriculum.visibility == Visibility.PUBLIC
        assert curriculum.updated_at > old_updated_at

    def test_make_public_success(self):
        """공개로 변경 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()

        # When
        curriculum.make_public()

        # Then
        assert curriculum.is_public()
        assert not curriculum.is_private()

    def test_make_private_success(self):
        """비공개로 변경 성공 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        curriculum.make_public()  # 먼저 공개로 변경

        # When
        curriculum.make_private()

        # Then
        assert curriculum.is_private()
        assert not curriculum.is_public()

    def test_is_owned_by_success(self):
        """소유자 확인 성공 테스트"""
        # Given
        owner_id = "valid_owner_id"
        curriculum = self._create_valid_curriculum(owner_id=owner_id)

        # When & Then
        assert curriculum.is_owned_by(owner_id)
        assert not curriculum.is_owned_by("different_owner_id")

    def test_get_total_weeks(self):
        """전체 주차 수 조회 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        curriculum.add_week_schedule(
            WeekSchedule(
                week_number=WeekNumber(2),
                title=Title("개념"),
                lessons=Lessons(["Week 2 lesson"]),
            )
        )

        # When
        total_weeks = curriculum.get_total_weeks()

        # Then
        assert total_weeks == 2

    def test_get_total_lessons(self):
        """전체 레슨 수 조회 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()
        curriculum.add_week_schedule(
            WeekSchedule(
                week_number=WeekNumber(2),
                title=Title("개념"),
                lessons=Lessons(["Lesson 1", "Lesson 2", "Lesson 3"]),
            )
        )

        # When
        total_lessons = curriculum.get_total_lessons()

        # Then
        assert total_lessons == 5  # 2 + 3

    def test_has_week_success(self):
        """주차 존재 여부 확인 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()

        # When & Then
        assert curriculum.has_week(WeekNumber(1))
        assert not curriculum.has_week(WeekNumber(5))

    def test_is_empty(self):
        """빈 커리큘럼 확인 테스트"""
        # Given
        empty_curriculum = Curriculum(
            id="curriculum_id",
            owner_id="owner_id",
            title=Title("Empty Curriculum"),
            visibility=Visibility.PRIVATE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            week_schedules=[],
        )
        non_empty_curriculum = self._create_valid_curriculum()

        # When & Then
        assert empty_curriculum.is_empty()
        assert not non_empty_curriculum.is_empty()

    def test_week_schedules_sorted_by_week_number(self):
        """주차 스케줄이 주차 번호 순으로 정렬되는지 테스트"""
        # Given
        curriculum = self._create_valid_curriculum()

        # 역순으로 추가
        curriculum.add_week_schedule(
            WeekSchedule(
                week_number=WeekNumber(3),
                title=Title("개념"),
                lessons=Lessons(["Week 3 lesson"]),
            )
        )
        curriculum.add_week_schedule(
            WeekSchedule(
                week_number=WeekNumber(2),
                title=Title("개념"),
                lessons=Lessons(["Week 2 lesson"]),
            )
        )

        # When
        week_numbers = curriculum.get_week_numbers()

        # Then
        assert week_numbers == [1, 2, 3]

    def _create_valid_curriculum(self, owner_id: str = "valid_owner_id") -> Curriculum:
        """유효한 커리큘럼 생성 헬퍼 메서드"""
        now = datetime.now(timezone.utc)
        return Curriculum(
            id="valid_curriculum_id",
            owner_id=owner_id,
            title=Title("Test Curriculum"),
            visibility=Visibility.PRIVATE,
            created_at=now,
            updated_at=now,
            week_schedules=[
                WeekSchedule(
                    week_number=WeekNumber(1),
                    title=Title("개념"),
                    lessons=Lessons(["Lesson 1", "Lesson 2"]),
                )
            ],
        )
