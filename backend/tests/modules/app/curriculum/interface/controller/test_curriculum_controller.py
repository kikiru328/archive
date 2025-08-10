import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, status

from app.modules.curriculum.interface.controller.curriculum_controller import (
    curriculum_router,
    week_router,
    lesson_router,
)
from app.modules.curriculum.application.service.curriculum_service import (
    CurriculumService,
)
from app.modules.curriculum.application.dto.curriculum_dto import (
    CurriculumDTO,
    CurriculumPageDTO,
    CurriculumBriefDTO,
    WeekScheduleDTO,
)
from app.modules.curriculum.application.exception import (
    CurriculumNotFoundError,
    CurriculumCountOverError,
    WeekScheduleNotFoundError,
    WeekIndexOutOfRangeError,
    LLMGenerationError,
)
from app.core.auth import CurrentUser, Role


@pytest.fixture
def mock_curriculum_service():
    """CurriculumService 모킹"""
    return AsyncMock(spec=CurriculumService)


@pytest.fixture
def mock_current_user():
    """현재 사용자 모킹"""
    return CurrentUser(id="test_user_id", role=Role.USER)


@pytest.fixture
def sample_curriculum_dto():
    """샘플 CurriculumDTO"""
    return CurriculumDTO(
        id="01HKQJQJQJQJQJQJQJQJQJ",
        owner_id="test_user_id",
        title="Python 기초 과정",
        visibility="PRIVATE",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        week_schedules=[
            WeekScheduleDTO(
                week_number=1, title="개념", lessons=["기초 개념", "환경 설정"]
            ),
            WeekScheduleDTO(week_number=2, title="개념", lessons=["심화 학습", "실습"]),
        ],
    )


@pytest.fixture
def sample_curriculum_page_dto():
    """샘플 CurriculumPageDTO"""
    brief_dto = CurriculumBriefDTO(
        id="01HKQJQJQJQJQJQJQJQJQJ",
        owner_id="test_user_id",
        title="Python 기초 과정",
        visibility="PRIVATE",
        total_weeks=2,
        total_lessons=4,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return CurriculumPageDTO(
        total_count=1,
        page=1,
        items_per_page=10,
        curriculums=[brief_dto],
    )


@pytest.fixture
def app_with_overrides(
    mock_curriculum_service: AsyncMock, mock_current_user: CurrentUser
) -> FastAPI:
    """의존성이 오버라이드된 FastAPI 앱"""
    from app.core.di_container import Container
    from app.core.auth import get_current_user

    app = FastAPI()

    # Container override
    container = Container()
    container.curriculum_service.override(mock_curriculum_service)  # type: ignore

    # Router에 Container를 연결
    container.wire(packages=["app.modules.curriculum.interface.controller"])

    app.include_router(curriculum_router, prefix="/api/v1")
    app.include_router(week_router, prefix="/api/v1")
    app.include_router(lesson_router, prefix="/api/v1")

    # get_current_user override
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    return app


@pytest.fixture
def client(app_with_overrides: FastAPI):
    """테스트 클라이언트 픽스처"""
    return TestClient(app_with_overrides)


class TestCurriculumController:
    """커리큘럼 컨트롤러 테스트"""

    def test_create_curriculum_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """커리큘럼 생성 성공 테스트"""
        # Given
        mock_curriculum_service.create_curriculum.return_value = sample_curriculum_dto

        create_data = {
            "title": "Python 기초 과정",
            "week_schedules": [
                {"week_number": 1, "lessons": ["기초 개념", "환경 설정"]},
                {"week_number": 2, "lessons": ["심화 학습", "실습"]},
            ],
            "visibility": "PRIVATE",
        }

        # When
        response = client.post("/api/v1/curriculums", json=create_data)

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Python 기초 과정"
        assert data["visibility"] == "PRIVATE"
        assert len(data["week_schedules"]) == 2

    def test_create_curriculum_count_limit_exceeded(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """커리큘럼 개수 제한 초과 테스트"""
        # Given
        mock_curriculum_service.create_curriculum.side_effect = (
            CurriculumCountOverError("You can only have to 10 curriculums")
        )

        create_data = {
            "title": "Test Curriculum",
            "week_schedules": [{"week_number": 1, "lessons": ["Test lesson"]}],
        }

        # When & Then
        with pytest.raises(CurriculumCountOverError):
            client.post("/api/v1/curriculums", json=create_data)

    def test_generate_curriculum_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """AI 커리큘럼 생성 성공 테스트"""
        # Given
        mock_curriculum_service.generate_curriculum.return_value = sample_curriculum_dto

        generate_data = {
            "goal": "Python 기초 학습",
            "period": 4,
            "difficulty": "beginner",
            "details": "프로그래밍 입문자를 위한 과정",
        }

        # When
        response = client.post("/api/v1/curriculums/generate", json=generate_data)

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Python 기초 과정"

    def test_generate_curriculum_llm_error(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """LLM 에러 처리 테스트"""
        # Given
        mock_curriculum_service.generate_curriculum.side_effect = LLMGenerationError(
            "Failed to generate curriculum"
        )

        generate_data = {
            "goal": "Python 학습",
            "period": 2,
            "difficulty": "beginner",
            "details": "기초 과정",
        }

        # When & Then
        with pytest.raises(LLMGenerationError):
            client.post("/api/v1/curriculums/generate", json=generate_data)

    def test_get_curriculums_by_owner(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_page_dto: CurriculumPageDTO,
    ):
        """소유자별 커리큘럼 목록 조회 테스트"""
        # Given
        mock_curriculum_service.get_curriculums.return_value = (
            sample_curriculum_page_dto
        )

        # When
        response = client.get("/api/v1/curriculums/me?page=1&items_per_page=10")

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 1
        assert data["page"] == 1
        assert len(data["curriculums"]) == 1

    def test_get_public_curriculums(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_page_dto: CurriculumPageDTO,
    ):
        """공개 커리큘럼 목록 조회 테스트"""
        # Given
        mock_curriculum_service.get_curriculums.return_value = (
            sample_curriculum_page_dto
        )

        # When
        response = client.get("/api/v1/curriculums/public?public=true")

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 1

    def test_get_curriculum_by_id_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """커리큘럼 상세 조회 성공 테스트"""
        # Given
        mock_curriculum_service.get_curriculum_by_id.return_value = (
            sample_curriculum_dto
        )

        # When
        response = client.get("/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ")

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "01HKQJQJQJQJQJQJQJQJQJ"
        assert data["title"] == "Python 기초 과정"

    def test_get_curriculum_by_id_not_found(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """존재하지 않는 커리큘럼 조회 테스트"""
        # Given
        mock_curriculum_service.get_curriculum_by_id.side_effect = (
            CurriculumNotFoundError("Curriculum not found")
        )

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            client.get("/api/v1/curriculums/nonexistent")

    def test_update_curriculum_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """커리큘럼 수정 성공 테스트"""
        # Given
        updated_dto = CurriculumDTO(
            id=sample_curriculum_dto.id,
            owner_id=sample_curriculum_dto.owner_id,
            title="수정된 제목",
            visibility="PUBLIC",
            created_at=sample_curriculum_dto.created_at,
            updated_at=datetime.now(timezone.utc),
            week_schedules=sample_curriculum_dto.week_schedules,
        )
        mock_curriculum_service.update_curriculum.return_value = updated_dto

        update_data = {"title": "수정된 제목", "visibility": "PUBLIC"}

        # When
        response = client.patch(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ", json=update_data
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "수정된 제목"
        assert data["visibility"] == "PUBLIC"

    def test_update_curriculum_not_found(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """존재하지 않는 커리큘럼 수정 테스트"""
        # Given
        mock_curriculum_service.update_curriculum.side_effect = CurriculumNotFoundError(
            "Curriculum not found"
        )

        update_data = {"title": "수정된 제목"}

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            client.patch("/api/v1/curriculums/nonexistent", json=update_data)

    def test_delete_curriculum_success(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """커리큘럼 삭제 성공 테스트"""
        # Given
        mock_curriculum_service.delete_curriculum.return_value = None

        # When
        response = client.delete("/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ")

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_curriculum_not_found(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """존재하지 않는 커리큘럼 삭제 테스트"""
        # Given
        mock_curriculum_service.delete_curriculum.side_effect = CurriculumNotFoundError(
            "Curriculum not found"
        )

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            client.delete("/api/v1/curriculums/nonexistent")


class TestWeekController:
    """주차 컨트롤러 테스트"""

    def test_create_week_schedule_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """주차 생성 성공 테스트"""
        # Given
        mock_curriculum_service.create_week_schedule.return_value = (
            sample_curriculum_dto
        )

        week_data = {
            "week_number": 3,
            "lessons": ["새로운 주차 레슨1", "새로운 주차 레슨2"],
        }

        # When
        response = client.post(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks", json=week_data
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "01HKQJQJQJQJQJQJQJQJQJ"

    def test_create_week_schedule_curriculum_not_found(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """존재하지 않는 커리큘럼에 주차 생성 테스트"""
        # Given
        mock_curriculum_service.create_week_schedule.side_effect = (
            CurriculumNotFoundError("Curriculum not found")
        )

        week_data = {"week_number": 1, "lessons": ["새 레슨"]}

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            client.post("/api/v1/curriculums/nonexistent/weeks", json=week_data)

    def test_delete_week_schedule_success(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """주차 삭제 성공 테스트"""
        # Given
        mock_curriculum_service.delete_week_schedule.return_value = None

        # When
        response = client.delete("/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1")

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_week_schedule_not_found(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """존재하지 않는 주차 삭제 테스트"""
        # Given
        mock_curriculum_service.delete_week_schedule.side_effect = (
            WeekScheduleNotFoundError("Week not found")
        )

        # When & Then
        with pytest.raises(WeekScheduleNotFoundError):
            client.delete("/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/999")


class TestLessonController:
    """레슨 컨트롤러 테스트"""

    def test_create_lesson_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """레슨 생성 성공 테스트"""
        # Given
        # 실제 CurriculumDTO 객체 반환하도록 설정
        mock_curriculum_service.create_lesson.return_value = sample_curriculum_dto

        lesson_data = {"lesson": "새로운 레슨", "lesson_index": 1}

        # When
        response = client.post(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1/lessons",
            json=lesson_data,
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "01HKQJQJQJQJQJQJQJQJQJ"

    def test_create_lesson_week_not_found(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """존재하지 않는 주차에 레슨 생성 테스트"""
        # Given
        mock_curriculum_service.create_lesson.side_effect = WeekScheduleNotFoundError(
            "Week not found"
        )

        lesson_data = {"lesson": "새로운 레슨"}

        # When & Then
        with pytest.raises(WeekScheduleNotFoundError):
            client.post(
                "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/999/lessons",
                json=lesson_data,
            )

    def test_update_lesson_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """레슨 수정 성공 테스트"""
        # Given
        mock_curriculum_service.update_lesson.return_value = sample_curriculum_dto

        lesson_data = {"lesson": "수정된 레슨"}

        # When
        response = client.put(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1/lessons/0",
            json=lesson_data,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "01HKQJQJQJQJQJQJQJQJQJ"

    def test_update_lesson_index_out_of_range(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """레슨 인덱스 범위 초과 테스트"""
        # Given
        mock_curriculum_service.update_lesson.side_effect = WeekIndexOutOfRangeError(
            "Lesson index out of range"
        )

        lesson_data = {"lesson": "수정 시도"}

        # When & Then
        with pytest.raises(WeekIndexOutOfRangeError):
            client.put(
                "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1/lessons/999",
                json=lesson_data,
            )

    def test_delete_lesson_success(
        self,
        client: TestClient,
        mock_curriculum_service: AsyncMock,
        sample_curriculum_dto: CurriculumDTO,
    ):
        """레슨 삭제 성공 테스트"""
        # Given
        mock_curriculum_service.delete_lesson.return_value = sample_curriculum_dto

        # When
        response = client.delete(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1/lessons/0"
        )

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_lesson_index_out_of_range(
        self, client: TestClient, mock_curriculum_service: AsyncMock
    ):
        """레슨 인덱스 범위 초과 삭제 테스트"""
        # Given
        mock_curriculum_service.delete_lesson.side_effect = WeekIndexOutOfRangeError(
            "Lesson index out of range"
        )

        # When & Then
        with pytest.raises(WeekIndexOutOfRangeError):
            client.delete(
                "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1/lessons/999"
            )


class TestValidationErrors:
    """유효성 검증 오류 테스트"""

    def test_create_curriculum_invalid_data(self, client: TestClient):
        """잘못된 데이터로 커리큘럼 생성"""
        # Given
        invalid_data = {
            "title": "",  # 빈 제목 (2글자 이상 필요)
            "week_schedules": [],  # 빈 주차 목록 (1개 이상 필요)
        }

        # When
        response = client.post("/api/v1/curriculums", json=invalid_data)

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "detail" in error_detail

    def test_generate_curriculum_invalid_period(self, client: TestClient):
        """잘못된 기간으로 AI 커리큘럼 생성"""
        # Given
        invalid_data = {
            "goal": "Python 학습",
            "period": 0,  # 1-24 범위 벗어남
            "difficulty": "beginner",
        }

        # When
        response = client.post("/api/v1/curriculums/generate", json=invalid_data)

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "detail" in error_detail

    def test_create_week_invalid_week_number(self, client: TestClient):
        """잘못된 주차 번호로 주차 생성"""
        # Given
        invalid_data = {"week_number": 0, "lessons": ["레슨"]}  # 1 이상이어야 함

        # When
        response = client.post(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks", json=invalid_data
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "detail" in error_detail

    def test_create_lesson_missing_lesson_field(self, client: TestClient):
        """레슨 필드 누락으로 레슨 생성"""
        # Given
        invalid_data = {}  # lesson 필드 누락

        # When
        response = client.post(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1/lessons",
            json=invalid_data,
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "detail" in error_detail

    def test_create_curriculum_title_too_long(self, client: TestClient):
        """제목이 너무 긴 커리큘럼 생성"""
        # Given
        invalid_data = {
            "title": "A" * 51,  # 50글자 초과
            "week_schedules": [{"week_number": 1, "lessons": ["Test lesson"]}],
        }

        # When
        response = client.post("/api/v1/curriculums", json=invalid_data)

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_generate_curriculum_invalid_difficulty(self, client: TestClient):
        """잘못된 난이도로 AI 커리큘럼 생성"""
        # Given
        invalid_data = {
            "goal": "Python 학습",
            "period": 4,
            "difficulty": "invalid_level",  # 유효하지 않은 난이도
        }

        # When
        response = client.post("/api/v1/curriculums/generate", json=invalid_data)

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_week_empty_lessons(self, client: TestClient):
        """빈 레슨 목록으로 주차 생성"""
        # Given
        invalid_data = {"week_number": 1, "lessons": []}  # 빈 레슨 목록 (1개 이상 필요)

        # When
        response = client.post(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks", json=invalid_data
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_lesson_negative_index(self, client: TestClient):
        """음수 인덱스로 레슨 생성"""
        # Given
        invalid_data = {"lesson": "새로운 레슨", "lesson_index": -1}  # 0 이상이어야 함

        # When
        response = client.post(
            "/api/v1/curriculums/01HKQJQJQJQJQJQJQJQJQJ/weeks/1/lessons",
            json=invalid_data,
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthenticationRequired:
    """인증 필요 테스트"""

    def test_endpoints_require_authentication(self):
        """모든 엔드포인트가 인증을 요구하는지 확인"""
        # 의존성 오버라이드 없는 순수 클라이언트 생성
        app = FastAPI()
        app.include_router(curriculum_router, prefix="/api/v1")
        app.include_router(week_router, prefix="/api/v1")
        app.include_router(lesson_router, prefix="/api/v1")
        client = TestClient(app)

        endpoints = [
            ("POST", "/api/v1/curriculums"),
            ("POST", "/api/v1/curriculums/generate"),
            ("GET", "/api/v1/curriculums/me"),
            ("GET", "/api/v1/curriculums/public"),
            ("GET", "/api/v1/curriculums/test_id"),
            ("PATCH", "/api/v1/curriculums/test_id"),
            ("DELETE", "/api/v1/curriculums/test_id"),
            ("POST", "/api/v1/curriculums/test_id/weeks"),
            ("DELETE", "/api/v1/curriculums/test_id/weeks/1"),
            ("POST", "/api/v1/curriculums/test_id/weeks/1/lessons"),
            ("PUT", "/api/v1/curriculums/test_id/weeks/1/lessons/0"),
            ("DELETE", "/api/v1/curriculums/test_id/weeks/1/lessons/0"),
        ]

        for method, url in endpoints:
            # When
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json={})
            elif method == "PATCH":
                response = client.patch(url, json={})
            elif method == "PUT":
                response = client.put(url, json={})
            elif method == "DELETE":
                response = client.delete(url)

            # Then
            assert response.status_code == status.HTTP_401_UNAUTHORIZED  # type: ignore
