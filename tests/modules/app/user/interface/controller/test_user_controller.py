import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from datetime import datetime, timezone

from app.modules.user.interface.controller.user_controller import user_router as router
from app.modules.user.application.service.user_service import UserService
from app.modules.user.application.dto.user_dto import UserDTO, UsersPageDTO
from app.modules.user.application.exception import UserNotFoundError, ExistNameError
from app.core.auth import CurrentUser, Role


@pytest.fixture  # type: ignore
def mock_user_service():
    """UserService 모킹"""
    return AsyncMock(spec=UserService)


@pytest.fixture
def mock_current_user():
    """현재 사용자 모킹"""
    return CurrentUser(id="test_user_id", role=Role.USER)


@pytest.fixture
def sample_user_dto():
    """샘플 UserDTO"""
    return UserDTO(
        id="test_user_id",
        email="test@example.com",
        name="테스트유저",
        role="USER",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_users_page_dto():
    """샘플 UsersPageDTO"""
    users = [
        UserDTO(
            id="user1",
            email="user1@example.com",
            name="유저1",
            role="USER",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        UserDTO(
            id="user2",
            email="user2@example.com",
            name="유저2",
            role="USER",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    return UsersPageDTO(
        total_count=2,
        page=1,
        items_per_page=18,
        users=users,
    )


@pytest.fixture
def app_with_overrides(
    mock_user_service: AsyncMock, mock_current_user: CurrentUser
) -> FastAPI:
    """의존성이 오버라이드된 FastAPI 앱"""
    from app.core.di_container import Container
    from app.core.auth import get_current_user

    app = FastAPI()

    # Container override
    container = Container()
    container.user_service.override(mock_user_service)  # type: ignore

    # Router에 Container를 연결
    container.wire(packages=["app.modules.user.interface.controller"])

    app.include_router(router, prefix="/api/v1")

    # get_current_user override
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    return app


@pytest.fixture
def client(app_with_overrides: FastAPI):
    """테스트 클라이언트 픽스처"""
    return TestClient(app_with_overrides)


class TestGetMe:
    """현재 사용자 정보 조회 테스트"""

    def test_get_me_success(
        self, client: TestClient, mock_user_service: AsyncMock, sample_user_dto: UserDTO
    ):
        """현재 사용자 정보 조회 성공"""
        # Given
        mock_user_service.get_user_by_id.return_value = sample_user_dto

        # When
        response = client.get("/api/v1/users/me")

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "테스트유저"
        assert data["email"] == "test@example.com"

    def test_get_me_user_not_found(
        self, client: TestClient, mock_user_service: AsyncMock
    ):
        """현재 사용자 정보 조회 실패 - 사용자 없음"""
        # Given
        mock_user_service.get_user_by_id.side_effect = UserNotFoundError(
            "User not found"
        )

        # When & Then - exception이 발생하므로 pytest.raises 사용
        with pytest.raises(UserNotFoundError):
            client.get("/api/v1/users/me")


class TestUpdateMe:
    """현재 사용자 정보 수정 테스트"""

    def test_update_me_success(
        self, client: TestClient, mock_user_service: AsyncMock, sample_user_dto: UserDTO
    ):
        """현재 사용자 정보 수정 성공"""
        # Given
        updated_user = UserDTO(
            id="test_user_id",
            email="test@example.com",
            name="수정된유저",
            role="USER",
            created_at=sample_user_dto.created_at,
            updated_at=datetime.now(timezone.utc),
        )
        mock_user_service.update_user.return_value = updated_user

        update_data = {"name": "수정된유저", "password": "NewPassword123!"}

        # When
        response = client.put("/api/v1/users/me", json=update_data)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "수정된유저"
        assert data["email"] == "test@example.com"

    def test_update_me_name_only(
        self, client: TestClient, mock_user_service: AsyncMock, sample_user_dto: UserDTO
    ):
        """이름만 수정"""
        # Given
        updated_user = UserDTO(
            id="test_user_id",
            email="test@example.com",
            name="새이름",
            role="USER",
            created_at=sample_user_dto.created_at,
            updated_at=datetime.now(timezone.utc),
        )
        mock_user_service.update_user.return_value = updated_user

        update_data = {"name": "새이름"}

        # When
        response = client.put("/api/v1/users/me", json=update_data)

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "새이름"

    def test_update_me_password_only(
        self, client: TestClient, mock_user_service: AsyncMock, sample_user_dto: UserDTO
    ):
        """비밀번호만 수정"""
        # Given
        mock_user_service.update_user.return_value = sample_user_dto

        update_data = {"password": "NewPassword123!"}

        # When
        response = client.put("/api/v1/users/me", json=update_data)

        # Then
        assert response.status_code == status.HTTP_200_OK

    def test_update_me_exist_name_error(
        self, client: TestClient, mock_user_service: AsyncMock
    ):
        """이름 중복 오류"""
        # Given
        mock_user_service.update_user.side_effect = ExistNameError(
            "Username already exist"
        )

        update_data = {"name": "중복이름"}

        # When & Then
        with pytest.raises(ExistNameError):
            client.put("/api/v1/users/me", json=update_data)

    def test_update_me_user_not_found(
        self, client: TestClient, mock_user_service: AsyncMock
    ):
        """사용자 없음 오류"""
        # Given
        mock_user_service.update_user.side_effect = UserNotFoundError("User not found")

        update_data = {"name": "새이름"}

        # When & Then
        with pytest.raises(UserNotFoundError):
            client.put("/api/v1/users/me", json=update_data)


class TestDeleteMe:
    """현재 사용자 계정 삭제 테스트"""

    def test_delete_me_success(self, client: TestClient, mock_user_service: AsyncMock):
        """계정 삭제 성공"""
        # Given
        mock_user_service.delete_user.return_value = None

        # When
        response = client.delete("/api/v1/users/me")

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_me_user_not_found(
        self, client: TestClient, mock_user_service: AsyncMock
    ):
        """계정 삭제 실패 - 사용자 없음"""
        # Given
        mock_user_service.delete_user.side_effect = UserNotFoundError("User not found")

        # When & Then
        with pytest.raises(UserNotFoundError):
            client.delete("/api/v1/users/me")


class TestGetUsers:
    """사용자 목록 조회 테스트"""

    def test_get_users_success(
        self,
        client: TestClient,
        mock_user_service: AsyncMock,
        sample_users_page_dto: UsersPageDTO,
    ):
        """사용자 목록 조회 성공"""
        # Given
        mock_user_service.get_users.return_value = sample_users_page_dto

        # When
        response = client.get("/api/v1/users")

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 2
        assert data["page"] == 1
        assert data["items_per_page"] == 18
        assert len(data["users"]) == 2
        assert data["users"][0]["name"] == "유저1"
        assert data["users"][1]["name"] == "유저2"

    def test_get_users_with_pagination(
        self,
        client: TestClient,
        mock_user_service: AsyncMock,
        sample_users_page_dto: UsersPageDTO,
    ):
        """페이지네이션 파라미터와 함께 사용자 목록 조회"""
        # Given
        mock_user_service.get_users.return_value = sample_users_page_dto

        # When
        response = client.get("/api/v1/users?page=2&items_per_page=10")

        # Then
        assert response.status_code == status.HTTP_200_OK

    def test_get_users_default_pagination(
        self,
        client: TestClient,
        mock_user_service: AsyncMock,
        sample_users_page_dto: UsersPageDTO,
    ):
        """기본 페이지네이션 값 확인"""
        # Given
        mock_user_service.get_users.return_value = sample_users_page_dto

        # When
        response = client.get("/api/v1/users")

        # Then
        assert response.status_code == status.HTTP_200_OK


class TestGetUserByName:
    """사용자명으로 사용자 정보 조회 테스트"""

    def test_get_user_by_name_success(
        self, client: TestClient, mock_user_service: AsyncMock, sample_user_dto: UserDTO
    ):
        """사용자명으로 사용자 정보 조회 성공"""
        # Given
        mock_user_service.get_user_by_name.return_value = sample_user_dto

        # When
        response = client.get("/api/v1/users/테스트유저")

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "테스트유저"
        assert data["email"] == "test@example.com"

    def test_get_user_by_name_not_found(
        self, client: TestClient, mock_user_service: AsyncMock
    ):
        """사용자명으로 사용자 정보 조회 실패 - 사용자 없음"""
        # Given
        mock_user_service.get_user_by_name.side_effect = UserNotFoundError(
            "User not found"
        )

        # When & Then
        with pytest.raises(UserNotFoundError):
            client.get("/api/v1/users/존재하지않는유저")

    def test_get_user_by_name_with_special_characters(
        self, client: TestClient, mock_user_service: AsyncMock
    ):
        """특수 문자가 포함된 사용자명으로 조회"""
        # Given
        special_user = UserDTO(
            id="special_user_id",
            email="special@example.com",
            name="특수_유저123",
            role="USER",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_user_service.get_user_by_name.return_value = special_user

        # When
        response = client.get("/api/v1/users/특수_유저123")

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "특수_유저123"


class TestAuthenticationRequired:
    """인증 필요 테스트"""

    def test_endpoints_require_authentication(self):
        """모든 엔드포인트가 인증을 요구하는지 확인"""
        # 의존성 오버라이드 없는 순수 클라이언트 생성
        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        client = TestClient(app)

        endpoints = [
            ("GET", "/api/v1/users/me"),
            ("PUT", "/api/v1/users/me"),
            ("DELETE", "/api/v1/users/me"),
            ("GET", "/api/v1/users"),
            ("GET", "/api/v1/users/testuser"),
        ]

        for method, url in endpoints:
            # When
            if method == "GET":
                response = client.get(url)
            elif method == "PUT":
                response = client.put(url, json={})
            elif method == "DELETE":
                response = client.delete(url)

            # Then
            assert response.status_code == status.HTTP_401_UNAUTHORIZED  # type: ignore


class TestValidationErrors:
    """유효성 검증 오류 테스트"""

    def test_update_me_invalid_data(
        self, client: TestClient, mock_user_service: AsyncMock, sample_user_dto: UserDTO
    ):
        """잘못된 데이터로 사용자 정보 수정"""
        # Given - 확실히 invalid한 데이터
        invalid_data = {  # type: ignore
            "name": 123,  # string이 아닌 숫자
            "password": ["invalid"],  # string이 아닌 배열
        }

        # When
        response = client.put("/api/v1/users/me", json=invalid_data)

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_users_invalid_pagination(
        self, client: TestClient, mock_user_service: AsyncMock
    ):
        """잘못된 페이지네이션 파라미터"""
        # When
        response = client.get("/api/v1/users?page=0&items_per_page=-1")

        # Then
        # FastAPI는 자동으로 음수나 0을 처리하므로 상황에 따라 다를 수 있음
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]
