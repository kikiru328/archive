import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.app.modules.curriculum.interface.schema.curriculum_schema import (
    CreateCurriculumRequest,
    UpdateCurriculumRequest,
    CreateWeekScheduleRequest,
    CreateLessonRequest,
    UpdateLessonRequest,
    GenerateCurriculumRequest,
    CurriculumResponse,
    CurriculumBriefResponse,
    CurriculumsPageResponse,
    WeekScheduleRequest,
)
from backend.app.modules.curriculum.application.dto.curriculum_dto import (
    CreateCurriculumCommand,
    UpdateCurriculumCommand,
    CreateWeekScheduleCommand,
    CreateLessonCommand,
    UpdateLessonCommand,
    GenerateCurriculumCommand,
    CurriculumDTO,
    CurriculumBriefDTO,
    CurriculumPageDTO,
    WeekScheduleDTO,
)
from backend.app.modules.curriculum.domain.vo.difficulty import Difficulty
from backend.app.modules.curriculum.domain.vo.visibility import Visibility


class TestWeekScheduleRequest:
    """WeekScheduleRequest 스키마 테스트"""

    def test_valid_week_schedule_request(self):
        """유효한 주차 스케줄 요청 테스트"""
        # Given
        data = {"week_number": 1, "lessons": ["Python 기초", "변수와 자료형"]}

        # When
        request = WeekScheduleRequest(**data)  # type: ignore

        # Then
        assert request.week_number == 1
        assert request.lessons == ["Python 기초", "변수와 자료형"]

    def test_invalid_week_number(self):
        """잘못된 주차 번호 테스트"""
        # Given
        data = {"week_number": 0, "lessons": ["Test lesson"]}  # 1 이상이어야 함

        # When & Then
        with pytest.raises(ValidationError):
            WeekScheduleRequest(**data)  # type: ignore

    def test_empty_lessons(self):
        """빈 레슨 목록 테스트"""
        # Given
        data = {"week_number": 1, "lessons": []}  # 최소 1개 이상이어야 함

        # When & Then
        with pytest.raises(ValidationError):
            WeekScheduleRequest(**data)  # type: ignore


class TestCreateCurriculumRequest:
    """CreateCurriculumRequest 스키마 테스트"""

    def test_valid_create_curriculum_request(self):
        """유효한 커리큘럼 생성 요청 테스트"""
        # Given
        data = {
            "title": "Python 기초 과정",
            "week_schedules": [
                {"week_number": 1, "lessons": ["기초 개념", "환경 설정"]},
                {"week_number": 2, "lessons": ["심화 학습", "실습"]},
            ],
            "visibility": "PRIVATE",
        }

        # When
        request = CreateCurriculumRequest(**data)  # type: ignore

        # Then
        assert request.title == "Python 기초 과정"
        assert len(request.week_schedules) == 2
        assert request.visibility == Visibility.PRIVATE

    def test_title_too_short(self):
        """제목이 너무 짧은 경우 테스트"""
        # Given
        data = {
            "title": "A",  # 2글자 이상이어야 함
            "week_schedules": [{"week_number": 1, "lessons": ["Test lesson"]}],
        }

        # When & Then
        with pytest.raises(ValidationError):
            CreateCurriculumRequest(**data)  # type: ignore

    def test_title_too_long(self):
        """제목이 너무 긴 경우 테스트"""
        # Given
        data = {
            "title": "A" * 51,  # 50글자 이하여야 함
            "week_schedules": [{"week_number": 1, "lessons": ["Test lesson"]}],
        }

        # When & Then
        with pytest.raises(ValidationError):
            CreateCurriculumRequest(**data)  # type: ignore

    def test_empty_week_schedules(self):
        """빈 주차 스케줄 테스트"""
        # Given
        data = {
            "title": "Test Curriculum",
            "week_schedules": [],  # 최소 1개 이상이어야 함
        }

        # When & Then
        with pytest.raises(ValidationError):
            CreateCurriculumRequest(**data)  # type: ignore

    def test_to_dto_conversion(self):
        """DTO 변환 테스트"""
        # Given
        data = {
            "title": "Python 기초 과정",
            "week_schedules": [
                {"week_number": 1, "lessons": ["기초 개념", "환경 설정"]},
            ],
            "visibility": "PUBLIC",
        }
        request = CreateCurriculumRequest(**data)  # type: ignore

        # When
        dto = request.to_dto(owner_id="test_user_id")

        # Then
        assert isinstance(dto, CreateCurriculumCommand)
        assert dto.owner_id == "test_user_id"
        assert dto.title == "Python 기초 과정"
        assert dto.visibility == Visibility.PUBLIC
        assert len(dto.week_schedules) == 1
        assert dto.week_schedules[0] == (1, ["기초 개념", "환경 설정"])


class TestUpdateCurriculumRequest:
    """UpdateCurriculumRequest 스키마 테스트"""

    def test_valid_update_request(self):
        """유효한 커리큘럼 수정 요청 테스트"""
        # Given
        data = {"title": "수정된 제목", "visibility": "PUBLIC"}

        # When
        request = UpdateCurriculumRequest(**data)  # type: ignore

        # Then
        assert request.title == "수정된 제목"
        assert request.visibility == Visibility.PUBLIC

    def test_partial_update_request(self):
        """부분 수정 요청 테스트"""
        # Given
        data = {
            "title": "새로운 제목"
            # visibility는 생략
        }

        # When
        request = UpdateCurriculumRequest(**data)  # type: ignore

        # Then
        assert request.title == "새로운 제목"
        assert request.visibility is None

    def test_empty_update_request(self):
        """빈 수정 요청 테스트"""
        # Given
        data = {}  # type: ignore

        # When
        request = UpdateCurriculumRequest(**data)  # type: ignore

        # Then
        assert request.title is None
        assert request.visibility is None

    def test_to_dto_conversion(self):
        """DTO 변환 테스트"""
        # Given
        data = {"title": "수정된 제목", "visibility": "PUBLIC"}
        request = UpdateCurriculumRequest(**data)  # type: ignore

        # When
        dto = request.to_dto(curriculum_id="test_id", owner_id="test_user_id")

        # Then
        assert isinstance(dto, UpdateCurriculumCommand)
        assert dto.curriculum_id == "test_id"
        assert dto.owner_id == "test_user_id"
        assert dto.title == "수정된 제목"
        assert dto.visibility == Visibility.PUBLIC


class TestGenerateCurriculumRequest:
    """GenerateCurriculumRequest 스키마 테스트"""

    def test_valid_generate_request(self):
        """유효한 AI 커리큘럼 생성 요청 테스트"""
        # Given
        data = {
            "goal": "Python 기초 학습",
            "period": 4,
            "difficulty": "beginner",
            "details": "프로그래밍 입문자를 위한 과정",
        }

        # When
        request = GenerateCurriculumRequest(**data)  # type: ignore

        # Then
        assert request.goal == "Python 기초 학습"
        assert request.period == 4
        assert request.difficulty == Difficulty.BEGINNER
        assert request.details == "프로그래밍 입문자를 위한 과정"

    def test_period_validation(self):
        """기간 유효성 검증 테스트"""
        # Given - 유효하지 않은 기간
        invalid_periods = [0, 25, -1]

        for period in invalid_periods:
            data = {"goal": "Test goal", "period": period, "difficulty": "beginner"}

            # When & Then
            with pytest.raises(ValidationError):
                GenerateCurriculumRequest(**data)  # type: ignore

    def test_valid_period_boundaries(self):
        """기간 경계값 테스트"""
        # Given - 유효한 기간 경계값
        valid_periods = [1, 24]

        for period in valid_periods:
            data = {"goal": "Test goal", "period": period, "difficulty": "beginner"}

            # When
            request = GenerateCurriculumRequest(**data)  # type: ignore

            # Then
            assert request.period == period

    def test_difficulty_validation(self):
        """난이도 유효성 검증 테스트"""
        # Given
        valid_difficulties = ["beginner", "intermediate", "expert"]

        for difficulty in valid_difficulties:
            data = {"goal": "Test goal", "period": 4, "difficulty": difficulty}

            # When
            request = GenerateCurriculumRequest(**data)  # type: ignore

            # Then
            assert request.difficulty == Difficulty(difficulty)

    def test_invalid_difficulty(self):
        """잘못된 난이도 테스트"""
        # Given
        data = {"goal": "Test goal", "period": 4, "difficulty": "invalid_difficulty"}

        # When & Then
        with pytest.raises(ValidationError):
            GenerateCurriculumRequest(**data)  # type: ignore

    def test_optional_details(self):
        """선택적 세부사항 테스트"""
        # Given
        data = {
            "goal": "Test goal",
            "period": 4,
            "difficulty": "beginner",
            # details 생략
        }

        # When
        request = GenerateCurriculumRequest(**data)  # type: ignore

        # Then
        assert request.details == ""

    def test_to_dto_conversion(self):
        """DTO 변환 테스트"""
        # Given
        data = {
            "goal": "Python 기초 학습",
            "period": 4,
            "difficulty": "intermediate",
            "details": "중급자를 위한 과정",
        }
        request = GenerateCurriculumRequest(**data)  # type: ignore

        # When
        dto = request.to_dto(owner_id="test_user_id")

        # Then
        assert isinstance(dto, GenerateCurriculumCommand)
        assert dto.owner_id == "test_user_id"
        assert dto.goal == "Python 기초 학습"
        assert dto.period == 4
        assert dto.difficulty == Difficulty.INTERMEDIATE
        assert dto.details == "중급자를 위한 과정"


class TestCreateWeekScheduleRequest:
    """CreateWeekScheduleRequest 스키마 테스트"""

    def test_valid_create_week_request(self):
        """유효한 주차 생성 요청 테스트"""
        # Given
        data = {"week_number": 3, "lessons": ["새로운 주차 레슨1", "새로운 주차 레슨2"]}

        # When
        request = CreateWeekScheduleRequest(**data)  # type: ignore

        # Then
        assert request.week_number == 3
        assert request.lessons == ["새로운 주차 레슨1", "새로운 주차 레슨2"]

    def test_to_dto_conversion(self):
        """DTO 변환 테스트"""
        # Given
        data = {"week_number": 2, "lessons": ["레슨1", "레슨2"]}
        request = CreateWeekScheduleRequest(**data)  # type: ignore

        # When
        dto = request.to_dto(curriculum_id="test_curriculum", owner_id="test_user")

        # Then
        assert isinstance(dto, CreateWeekScheduleCommand)
        assert dto.curriculum_id == "test_curriculum"
        assert dto.owner_id == "test_user"
        assert dto.week_number == 2
        assert dto.lessons == ["레슨1", "레슨2"]


class TestCreateLessonRequest:
    """CreateLessonRequest 스키마 테스트"""

    def test_valid_create_lesson_request(self):
        """유효한 레슨 생성 요청 테스트"""
        # Given
        data = {"lesson": "새로운 레슨", "lesson_index": 1}

        # When
        request = CreateLessonRequest(**data)  # type: ignore

        # Then
        assert request.lesson == "새로운 레슨"
        assert request.lesson_index == 1

    def test_optional_lesson_index(self):
        """선택적 레슨 인덱스 테스트"""
        # Given
        data = {
            "lesson": "새로운 레슨"
            # lesson_index 생략
        }

        # When
        request = CreateLessonRequest(**data)  # type: ignore

        # Then
        assert request.lesson == "새로운 레슨"
        assert request.lesson_index is None

    def test_negative_lesson_index_validation(self):
        """음수 레슨 인덱스 검증 테스트"""
        # Given
        data = {"lesson": "새로운 레슨", "lesson_index": -1}

        # When & Then
        with pytest.raises(ValidationError):
            CreateLessonRequest(**data)  # type: ignore

    def test_to_dto_conversion(self):
        """DTO 변환 테스트"""
        # Given
        data = {"lesson": "새로운 레슨", "lesson_index": 2}
        request = CreateLessonRequest(**data)  # type: ignore

        # When
        dto = request.to_dto(
            curriculum_id="test_curriculum", owner_id="test_user", week_number=1
        )

        # Then
        assert isinstance(dto, CreateLessonCommand)
        assert dto.curriculum_id == "test_curriculum"
        assert dto.owner_id == "test_user"
        assert dto.week_number == 1
        assert dto.lesson == "새로운 레슨"
        assert dto.lesson_index == 2


class TestUpdateLessonRequest:
    """UpdateLessonRequest 스키마 테스트"""

    def test_valid_update_lesson_request(self):
        """유효한 레슨 수정 요청 테스트"""
        # Given
        data = {"lesson": "수정된 레슨"}

        # When
        request = UpdateLessonRequest(**data)  # type: ignore

        # Then
        assert request.lesson == "수정된 레슨"

    def test_to_dto_conversion(self):
        """DTO 변환 테스트"""
        # Given
        data = {"lesson": "수정된 레슨"}
        request = UpdateLessonRequest(**data)  # type: ignore

        # When
        dto = request.to_dto(
            curriculum_id="test_curriculum",
            owner_id="test_user",
            week_number=1,
            lesson_index=0,
        )

        # Then
        assert isinstance(dto, UpdateLessonCommand)
        assert dto.curriculum_id == "test_curriculum"
        assert dto.owner_id == "test_user"
        assert dto.week_number == 1
        assert dto.lesson_index == 0
        assert dto.new_lesson == "수정된 레슨"


class TestCurriculumResponse:
    """CurriculumResponse 스키마 테스트"""

    def test_from_dto_conversion(self):
        """DTO에서 응답 모델로 변환 테스트"""
        # Given
        week_schedules = [
            WeekScheduleDTO(
                week_number=1, title="개념", lessons=["기초 개념", "환경 설정"]
            ),
            WeekScheduleDTO(week_number=2, title="개념", lessons=["심화 학습", "실습"]),
        ]

        dto = CurriculumDTO(
            id="test_id",
            owner_id="test_user",
            title="Python 기초 과정",
            visibility="PRIVATE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            week_schedules=week_schedules,
        )

        # When
        response = CurriculumResponse.from_dto(dto)

        # Then
        assert response.id == "test_id"
        assert response.owner_id == "test_user"
        assert response.title == "Python 기초 과정"
        assert response.visibility == Visibility.PRIVATE
        assert len(response.week_schedules) == 2
        assert response.week_schedules[0].week_number == 1
        assert response.week_schedules[0].lessons == ["기초 개념", "환경 설정"]


class TestCurriculumBriefResponse:
    """CurriculumBriefResponse 스키마 테스트"""

    def test_from_dto_conversion(self):
        """DTO에서 요약 응답 모델로 변환 테스트"""
        # Given
        dto = CurriculumBriefDTO(
            id="test_id",
            owner_id="test_user",
            title="Python 기초 과정",
            visibility="PUBLIC",
            total_weeks=4,
            total_lessons=12,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # When
        response = CurriculumBriefResponse.from_dto(dto)

        # Then
        assert response.id == "test_id"
        assert response.owner_id == "test_user"
        assert response.title == "Python 기초 과정"
        assert response.visibility == Visibility.PUBLIC
        assert response.total_weeks == 4
        assert response.total_lessons == 12


class TestCurriculumsPageResponse:
    """CurriculumsPageResponse 스키마 테스트"""

    def test_from_dto_conversion(self):
        """페이지 DTO에서 응답 모델로 변환 테스트"""
        # Given
        brief_dtos = [
            CurriculumBriefDTO(
                id="test_id_1",
                owner_id="test_user",
                title="Python 기초",
                visibility="PRIVATE",
                total_weeks=2,
                total_lessons=6,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            CurriculumBriefDTO(
                id="test_id_2",
                owner_id="test_user",
                title="Java 기초",
                visibility="PUBLIC",
                total_weeks=3,
                total_lessons=9,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]

        page_dto = CurriculumPageDTO(
            total_count=2, page=1, items_per_page=10, curriculums=brief_dtos
        )

        # When
        response = CurriculumsPageResponse.from_dto(page_dto)

        # Then
        assert response.total_count == 2
        assert response.page == 1
        assert response.items_per_page == 10
        assert len(response.curriculums) == 2
        assert response.curriculums[0].id == "test_id_1"
        assert response.curriculums[1].id == "test_id_2"


class TestSchemaValidationEdgeCases:
    """스키마 유효성 검증 엣지 케이스 테스트"""

    def test_unicode_characters_in_title(self):
        """제목에 유니코드 문자 포함 테스트"""
        # Given
        data = {
            "title": "파이썬 기초 과정 🐍",
            "week_schedules": [{"week_number": 1, "lessons": ["기초 개념"]}],
        }

        # When
        request = CreateCurriculumRequest(**data)  # type: ignore

        # Then
        assert request.title == "파이썬 기초 과정 🐍"

    def test_special_characters_in_lesson(self):
        """레슨에 특수 문자 포함 테스트"""
        # Given
        data = {"lesson": "HTML & CSS: 기초부터 심화까지 (1/3)"}

        # When
        request = CreateLessonRequest(**data)  # type: ignore

        # Then
        assert request.lesson == "HTML & CSS: 기초부터 심화까지 (1/3)"

    def test_very_long_lesson_names(self):
        """매우 긴 레슨 이름 테스트"""
        # Given
        long_lesson = "A" * 200  # 매우 긴 레슨 이름
        data = {"week_number": 1, "lessons": [long_lesson]}

        # When
        request = CreateWeekScheduleRequest(**data)  # type: ignore

        # Then
        assert request.lessons[0] == long_lesson

    def test_maximum_week_schedules(self):
        """최대 주차 스케줄 테스트"""
        # Given - 24주차까지
        week_schedules = []
        for i in range(1, 25):
            week_schedules.append({"week_number": i, "lessons": [f"Week {i} lesson"]})

        data = {"title": "장기간 과정", "week_schedules": week_schedules}

        # When
        request = CreateCurriculumRequest(**data)  # type: ignore

        # Then
        assert len(request.week_schedules) == 24

    def test_maximum_lessons_per_week(self):
        """주차당 최대 레슨 수 테스트"""
        # Given - 주차당 5개 레슨
        lessons = [f"Lesson {i}" for i in range(1, 6)]
        data = {"week_number": 1, "lessons": lessons}

        # When
        request = CreateWeekScheduleRequest(**data)  # type: ignore

        # Then
        assert len(request.lessons) == 5
