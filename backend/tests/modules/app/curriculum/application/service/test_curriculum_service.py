from typing import Tuple
from unittest.mock import AsyncMock, Mock, patch
import pytest
from ulid import ULID  # type: ignore
from datetime import datetime, timezone
from pytest_mock import MockerFixture

from app.common.llm.llm_client_repo import ILLMClientRepository
from app.modules.curriculum.application.dto.curriculum_dto import (
    CreateCurriculumCommand,
    GenerateCurriculumCommand,
    UpdateCurriculumCommand,
    CurriculumQuery,
    CurriculumDTO,
    CurriculumPageDTO,
)
from app.modules.curriculum.application.exception import (
    CurriculumCountOverError,
    CurriculumNotFoundError,
    LLMGenerationError,
)
from app.modules.curriculum.application.service.curriculum_service import (
    CurriculumService,
)
from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.curriculum.domain.service.curriculum_domain_service import (
    CurriculumDomainService,
)
from app.modules.curriculum.domain.vo import Title, Visibility, WeekNumber, Lessons
from app.modules.curriculum.domain.vo.difficulty import Difficulty
from app.modules.social.domain.repository.follow_repo import IFollowRepository
from app.modules.user.domain.vo.role import RoleVO


class TestCurriculumService:
    """CurriculumService 테스트"""

    @pytest.fixture
    def curriculum_service(self, mocker: MockerFixture) -> Tuple[
        CurriculumService,
        AsyncMock,
        Mock,
        AsyncMock,
        Mock,
    ]:
        """CurriculumService와 Mock 객체들을 반환"""
        mock_curriculum_repo: AsyncMock = mocker.AsyncMock(spec=ICurriculumRepository)
        mock_curriculum_domain_service: Mock = mocker.Mock(spec=CurriculumDomainService)
        mock_llm_client: AsyncMock = mocker.AsyncMock(spec=ILLMClientRepository)
        mock_follow_repo: AsyncMock = mocker.AsyncMock(spec=IFollowRepository)
        mock_ulid: Mock = mocker.Mock(spec=ULID)
        mock_ulid.generate.return_value = "01HKQJQJQJQJQJQJQJQJQJ"

        service = CurriculumService(
            curriculum_repo=mock_curriculum_repo,
            curriculum_domain_service=mock_curriculum_domain_service,
            llm_client=mock_llm_client,
            follow_repo=mock_follow_repo,
            ulid=mock_ulid,
        )

        return (
            service,
            mock_curriculum_repo,
            mock_curriculum_domain_service,
            mock_llm_client,
            mock_ulid,
        )

    @pytest.fixture
    def sample_curriculum(self) -> Curriculum:
        """테스트용 샘플 커리큘럼"""
        now: datetime = datetime.now(timezone.utc)
        week_schedules: list[WeekSchedule] = [
            WeekSchedule(
                week_number=WeekNumber(1),
                lessons=Lessons(["기초 개념", "환경 설정"]),
            ),
            WeekSchedule(
                week_number=WeekNumber(2),
                lessons=Lessons(["심화 학습", "실습"]),
            ),
        ]

        return Curriculum(
            id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            title=Title("테스트 커리큘럼"),
            visibility=Visibility.PRIVATE,
            created_at=now,
            updated_at=now,
            week_schedules=week_schedules,
        )

    @pytest.fixture
    def sample_llm_response(self) -> dict:  # type: ignore
        """테스트용 LLM 응답"""
        return {  # type: ignore
            "title": "Python 기초 커리큘럼",
            "schedule": [
                {"week_number": 1, "lessons": ["Python 소개", "개발환경 설정"]},
                {"week_number": 2, "lessons": ["변수와 자료형", "조건문"]},
                {"week_number": 3, "lessons": ["반복문", "함수"]},
                {"week_number": 4, "lessons": ["클래스", "모듈과 패키지"]},
            ],
        }

    # 커리큘럼 생성 테스트
    async def test_create_curriculum_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """커리큘럼 생성 성공 테스트"""
        # Given
        service, mock_repo, mock_domain_service, _, _ = curriculum_service
        command = CreateCurriculumCommand(
            owner_id="user_123",
            title="테스트 커리큘럼",
            week_schedules=[
                (1, ["기초 개념", "환경 설정"]),
                (2, ["심화 학습", "실습"]),
            ],
            visibility=Visibility.PRIVATE,
        )

        mock_repo.count_by_owner.return_value = 5
        mock_domain_service.create_curriculum.return_value = sample_curriculum
        mock_repo.save.return_value = None

        # When
        result = await service.create_curriculum(command)

        # Then
        assert isinstance(result, CurriculumDTO)
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"
        assert result.title == "테스트 커리큘럼"
        assert result.visibility == "PRIVATE"
        assert len(result.week_schedules) == 2

        mock_repo.count_by_owner.assert_called_once_with("user_123")
        mock_domain_service.create_curriculum.assert_called_once()
        mock_repo.save.assert_called_once_with(sample_curriculum)

    async def test_create_curriculum_count_limit_exceeded(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
    ) -> None:
        """커리큘럼 개수 제한 초과 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        command = CreateCurriculumCommand(
            owner_id="user_123",
            title="테스트 커리큘럼",
            week_schedules=[(1, ["기초 개념"])],
        )

        mock_repo.count_by_owner.return_value = 10

        # When & Then
        with pytest.raises(CurriculumCountOverError):
            await service.create_curriculum(command)

        mock_repo.save.assert_not_called()

    # AI 커리큘럼 생성 테스트
    async def test_generate_curriculum_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
        sample_llm_response: dict,  # type: ignore
        mocker: MockerFixture,
    ) -> None:
        """AI 커리큘럼 생성 성공 테스트"""
        # Given
        service, mock_repo, mock_domain_service, mock_llm_client, _ = curriculum_service
        command = GenerateCurriculumCommand(
            owner_id="user_123",
            goal="Python 기초 학습",
            period=4,
            difficulty=Difficulty.BEGINNER,
            details="프로그래밍 입문자를 위한 과정",
        )

        mock_repo.count_by_owner.return_value = 5
        mock_llm_client.generate_curriculum.return_value = sample_llm_response
        mock_domain_service.create_curriculum.return_value = sample_curriculum
        mock_repo.save.return_value = None

        # datetime.now을 모킹하여 일관된 타임스탬프 생성
        mock_datetime = mocker.patch(
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        )
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)

        # When
        result = await service.generate_curriculum(command)

        # Then
        assert isinstance(result, CurriculumDTO)
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"

        mock_llm_client.generate_curriculum.assert_called_once_with(
            goal="Python 기초 학습",
            period=4,
            difficulty=Difficulty.BEGINNER,
            details="프로그래밍 입문자를 위한 과정",
        )
        mock_domain_service.create_curriculum.assert_called_once()
        mock_repo.save.assert_called_once()

    async def test_generate_curriculum_llm_error(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
    ) -> None:
        """LLM 에러 처리 테스트"""
        # Given
        service, mock_repo, _, mock_llm_client, _ = curriculum_service
        command = GenerateCurriculumCommand(
            owner_id="user_123",
            goal="Python 학습",
            period=2,
            difficulty=Difficulty.BEGINNER,
            details="기초 과정",
        )

        mock_repo.count_by_owner.return_value = 5
        mock_llm_client.generate_curriculum.side_effect = Exception("LLM API Error")

        # When & Then
        with pytest.raises(LLMGenerationError):
            await service.generate_curriculum(command)

    # 커리큘럼 조회 테스트
    async def test_get_curriculums_by_owner(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """소유자별 커리큘럼 조회 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        query = CurriculumQuery(owner_id="user_123", page=1, items_per_page=10)
        mock_repo.find_by_owner_id.return_value = (1, [sample_curriculum])

        # When
        # result = await service.get_curriculums(query, RoleVO.USER)
        result = await service.get_curriculums(query)

        # Then
        assert isinstance(result, CurriculumPageDTO)
        assert result.total_count == 1
        assert result.page == 1
        assert len(result.curriculums) == 1
        assert result.curriculums[0].id == "01HKQJQJQJQJQJQJQJQJQJ"

        mock_repo.find_by_owner_id.assert_called_once_with(
            owner_id="user_123", page=1, items_per_page=10
        )

    async def test_get_public_curriculums(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """공개 커리큘럼 조회 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        query = CurriculumQuery(page=1, items_per_page=10)
        mock_repo.find_public_curriculums.return_value = (1, [sample_curriculum])

        # When
        # result = await service.get_curriculums(query, RoleVO.USER)
        result = await service.get_curriculums(query)

        # Then
        assert result.total_count == 1
        mock_repo.find_public_curriculums.assert_called_once_with(
            page=1, items_per_page=10
        )

    async def test_get_curriculum_by_id_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """커리큘럼 상세 조회 성공 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        mock_repo.find_by_id.return_value = sample_curriculum

        # When
        result = await service.get_curriculum_by_id(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            role=RoleVO.USER,
            owner_id="user_123",
        )

        # Then
        assert isinstance(result, CurriculumDTO)
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"
        mock_repo.find_by_id.assert_called_once_with(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            role=RoleVO.USER,
            owner_id="user_123",
        )

    async def test_get_curriculum_by_id_not_found(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
    ) -> None:
        """존재하지 않는 커리큘럼 조회 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        mock_repo.find_by_id.return_value = None

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            await service.get_curriculum_by_id(
                curriculum_id="nonexistent",
                role=RoleVO.USER,
                owner_id="user_123",
            )

    # 커리큘럼 수정 테스트
    async def test_update_curriculum_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """커리큘럼 수정 성공 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        command = UpdateCurriculumCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            title="수정된 제목",
            visibility=Visibility.PUBLIC,
        )

        mock_repo.find_by_id.return_value = sample_curriculum
        mock_repo.update.return_value = None

        # When
        result = await service.update_curriculum(command, RoleVO.USER)

        # Then
        assert isinstance(result, CurriculumDTO)
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"
        mock_repo.find_by_id.assert_called_once()
        mock_repo.update.assert_called_once()

    async def test_update_curriculum_not_found(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
    ) -> None:
        """존재하지 않는 커리큘럼 수정 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        command = UpdateCurriculumCommand(
            curriculum_id="nonexistent",
            owner_id="user_123",
            title="수정된 제목",
        )

        mock_repo.find_by_id.return_value = None

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            await service.update_curriculum(command, RoleVO.USER)

    async def test_update_curriculum_permission_denied(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """권한 없는 수정 시도 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        command = UpdateCurriculumCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="different_user",  # 다른 사용자
            title="수정된 제목",
        )

        mock_repo.find_by_id.return_value = sample_curriculum

        # When & Then
        with pytest.raises(PermissionError):
            await service.update_curriculum(command, RoleVO.USER)

    # 커리큘럼 삭제 테스트
    async def test_delete_curriculum_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """커리큘럼 삭제 성공 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        curriculum_id = "01HKQJQJQJQJQJQJQJQJQJ"
        owner_id = "user_123"

        mock_repo.find_by_id.return_value = sample_curriculum
        mock_repo.delete.return_value = None

        # When
        await service.delete_curriculum(curriculum_id, owner_id, RoleVO.USER)

        # Then
        mock_repo.find_by_id.assert_called_once()
        mock_repo.delete.assert_called_once_with(curriculum_id)

    async def test_delete_curriculum_permission_denied(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """권한 없는 삭제 시도 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        curriculum_id = "01HKQJQJQJQJQJQJQJQJQJ"
        owner_id = "different_user"  # 다른 사용자

        mock_repo.find_by_id.return_value = sample_curriculum

        # When & Then
        with pytest.raises(PermissionError):
            await service.delete_curriculum(curriculum_id, owner_id, RoleVO.USER)

        mock_repo.delete.assert_not_called()

    # LLM 응답 파싱 테스트
    def test_parse_valid_dict_response(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        mocker: MockerFixture,
    ) -> None:
        """유효한 딕셔너리 응답 파싱 테스트"""
        # Given
        service, _, _, _, _ = curriculum_service
        llm_response = {  # type: ignore
            "title": "Python 기초",
            "schedule": [
                {"week_number": 1, "lessons": ["변수", "연산자"]},
                {"week_number": 2, "lessons": ["조건문", "반복문"]},
            ],
        }

        # datetime.now 모킹
        mock_datetime = mocker.patch(
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        )
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)

        # When
        result = service._parse_llm_response(llm_response, "Python")  # type: ignore

        # Then
        assert "Python 기초" in result["title"]
        assert "240115" in result["title"]  # 타임스탬프 확인
        assert len(result["week_schedules"]) == 2
        assert result["week_schedules"][0] == (1, ["변수", "연산자"])

    def test_parse_list_response(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        mocker: MockerFixture,
    ) -> None:
        """리스트 형태 응답 파싱 테스트"""
        # Given
        service, _, _, _, _ = curriculum_service
        llm_response = [  # type: ignore
            {"week_number": 1, "lessons": ["기초"]},
            {"week_number": 2, "lessons": ["심화"]},
        ]

        # datetime.now 모킹
        mock_datetime = mocker.patch(
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        )
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)

        # When
        result = service._parse_llm_response(llm_response, "Test Goal")  # type: ignore

        # Then
        assert "Test Goal" in result["title"]
        assert len(result["week_schedules"]) == 2

    def test_parse_response_with_invalid_items(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        mocker: MockerFixture,
    ) -> None:
        """일부 잘못된 항목이 포함된 응답 파싱 테스트"""
        # Given
        service, _, _, _, _ = curriculum_service
        llm_response = {  # type: ignore
            "title": "Test",
            "schedule": [
                {"week_number": 1, "lessons": ["유효한 레슨"]},
                {
                    "week_number": "invalid",
                    "lessons": ["무효한 주차"],
                },  # 잘못된 주차 번호
                {"week_number": 2, "lessons": []},  # 빈 레슨 리스트
                {"week_number": 3, "lessons": ["유효한 레슨2"]},
            ],
        }

        # datetime.now 모킹
        mock_datetime = mocker.patch(
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        )
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)

        # When
        result = service._parse_llm_response(llm_response, "Test")  # type: ignore

        # Then
        # 유효한 항목만 포함되어야 함
        assert len(result["week_schedules"]) == 2
        assert result["week_schedules"][0] == (1, ["유효한 레슨"])
        assert result["week_schedules"][1] == (3, ["유효한 레슨2"])

    def test_parse_empty_response(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
    ) -> None:
        """빈 응답 처리 테스트"""
        # Given
        service, _, _, _, _ = curriculum_service
        llm_response = {"title": "Test", "schedule": []}  # type: ignore

        # When & Then
        with pytest.raises(LLMGenerationError):
            service._parse_llm_response(llm_response, "Test")  # type: ignore

    def test_parse_invalid_format_response(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
    ) -> None:
        """잘못된 형식 응답 처리 테스트"""
        # Given
        service, _, _, _, _ = curriculum_service
        llm_response = "invalid string response"

        # When & Then
        with pytest.raises(LLMGenerationError):
            service._parse_llm_response(llm_response, "Test")  # type: ignore


class TestCurriculumWeekManagement:
    """커리큘럼 주차 관리 테스트"""

    @pytest.fixture
    def curriculum_service(self, mocker: MockerFixture) -> Tuple[
        CurriculumService,
        AsyncMock,
        Mock,
        AsyncMock,
        Mock,
    ]:
        """CurriculumService와 Mock 객체들을 반환"""
        mock_curriculum_repo: AsyncMock = mocker.AsyncMock(spec=ICurriculumRepository)
        mock_curriculum_domain_service: Mock = mocker.Mock(spec=CurriculumDomainService)
        mock_llm_client: AsyncMock = mocker.AsyncMock(spec=ILLMClientRepository)
        mock_ulid: Mock = mocker.Mock(spec=ULID)
        mock_follow_repo: AsyncMock = mocker.AsyncMock(spec=IFollowRepository)
        mock_ulid.generate.return_value = "01HKQJQJQJQJQJQJQJQJQJ"

        service = CurriculumService(
            curriculum_repo=mock_curriculum_repo,
            curriculum_domain_service=mock_curriculum_domain_service,
            llm_client=mock_llm_client,
            follow_repo=mock_follow_repo,
            ulid=mock_ulid,
        )

        return (
            service,
            mock_curriculum_repo,
            mock_curriculum_domain_service,
            mock_llm_client,
            mock_ulid,
        )

    @pytest.fixture
    def sample_curriculum(self) -> Curriculum:
        """테스트용 샘플 커리큘럼"""
        now = datetime.now(timezone.utc)
        week_schedules = [
            WeekSchedule(
                week_number=WeekNumber(1),
                lessons=Lessons(["기초 개념", "환경 설정"]),
            ),
            WeekSchedule(
                week_number=WeekNumber(2),
                lessons=Lessons(["심화 학습", "실습"]),
            ),
        ]

        return Curriculum(
            id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            title=Title("테스트 커리큘럼"),
            visibility=Visibility.PRIVATE,
            created_at=now,
            updated_at=now,
            week_schedules=week_schedules,
        )

    async def test_create_week_schedule_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """주차 생성 성공 테스트"""
        # Given
        service, mock_repo, mock_domain_service, _, _ = curriculum_service
        from app.modules.curriculum.application.dto.curriculum_dto import (
            CreateWeekScheduleCommand,
        )

        command = CreateWeekScheduleCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            week_number=1,
            lessons=["새 레슨1", "새 레슨2"],
        )

        updated_curriculum = sample_curriculum  # 업데이트된 커리큘럼

        mock_repo.find_by_id.return_value = sample_curriculum
        mock_domain_service.insert_week_and_shift.return_value = updated_curriculum
        mock_repo.update.return_value = None

        # When
        result = await service.create_week_schedule(command, RoleVO.USER)

        # Then
        assert isinstance(result, CurriculumDTO)
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"

        mock_repo.find_by_id.assert_called_once()
        mock_domain_service.insert_week_and_shift.assert_called_once()
        mock_repo.update.assert_called_once_with(updated_curriculum)

    async def test_create_week_schedule_curriculum_not_found(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
    ) -> None:
        """존재하지 않는 커리큘럼에 주차 생성 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        from app.modules.curriculum.application.dto.curriculum_dto import (
            CreateWeekScheduleCommand,
        )

        command = CreateWeekScheduleCommand(
            curriculum_id="nonexistent",
            owner_id="user_123",
            week_number=1,
            lessons=["새 레슨"],
        )

        mock_repo.find_by_id.return_value = None

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            await service.create_week_schedule(command, RoleVO.USER)

    async def test_create_week_schedule_permission_denied(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """권한 없는 주차 생성 시도 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        from app.modules.curriculum.application.dto.curriculum_dto import (
            CreateWeekScheduleCommand,
        )

        command = CreateWeekScheduleCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="different_user",  # 다른 사용자
            week_number=1,
            lessons=["새 레슨"],
        )

        mock_repo.find_by_id.return_value = sample_curriculum

        # When & Then
        with pytest.raises(PermissionError):
            await service.create_week_schedule(command, RoleVO.USER)

    async def test_delete_week_schedule_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum: Curriculum,
    ) -> None:
        """주차 삭제 성공 테스트"""
        # Given
        service, mock_repo, mock_domain_service, _, _ = curriculum_service
        curriculum_id = "01HKQJQJQJQJQJQJQJQJQJ"
        owner_id = "user_123"
        week_number = 1

        updated_curriculum = sample_curriculum  # 업데이트된 커리큘럼

        mock_repo.find_by_id.return_value = sample_curriculum
        mock_domain_service.remove_week_and_shift.return_value = updated_curriculum
        mock_repo.update.return_value = None

        # When
        await service.delete_week_schedule(
            curriculum_id, owner_id, week_number, RoleVO.USER
        )

        # Then
        mock_repo.find_by_id.assert_called_once()
        mock_domain_service.remove_week_and_shift.assert_called_once()
        mock_repo.update.assert_called_once_with(updated_curriculum)


class TestCurriculumLessonManagement:
    """커리큘럼 레슨 관리 테스트"""

    @pytest.fixture
    def curriculum_service(self, mocker: MockerFixture) -> Tuple[
        CurriculumService,
        AsyncMock,
        Mock,
        AsyncMock,
        Mock,
    ]:
        """CurriculumService와 Mock 객체들을 반환"""
        mock_curriculum_repo: AsyncMock = mocker.AsyncMock(spec=ICurriculumRepository)
        mock_curriculum_domain_service: Mock = mocker.Mock(spec=CurriculumDomainService)
        mock_llm_client: AsyncMock = mocker.AsyncMock(spec=ILLMClientRepository)
        mock_ulid: Mock = mocker.Mock(spec=ULID)
        mock_follow_repo: AsyncMock = mocker.AsyncMock(spec=IFollowRepository)
        mock_ulid.generate.return_value = "01HKQJQJQJQJQJQJQJQJQJ"

        service = CurriculumService(
            curriculum_repo=mock_curriculum_repo,
            curriculum_domain_service=mock_curriculum_domain_service,
            llm_client=mock_llm_client,
            follow_repo=mock_follow_repo,
            ulid=mock_ulid,
        )

        return (
            service,
            mock_curriculum_repo,
            mock_curriculum_domain_service,
            mock_llm_client,
            mock_ulid,
        )

    @pytest.fixture
    def sample_curriculum_with_lessons(self) -> Curriculum:
        """레슨이 포함된 테스트용 커리큘럼"""
        now = datetime.now(timezone.utc)
        week_schedules = [
            WeekSchedule(
                week_number=WeekNumber(1),
                lessons=Lessons(["기초 개념", "환경 설정", "첫 번째 실습"]),
            ),
        ]

        return Curriculum(
            id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            title=Title("테스트 커리큘럼"),
            visibility=Visibility.PRIVATE,
            created_at=now,
            updated_at=now,
            week_schedules=week_schedules,
        )

    async def test_create_lesson_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum_with_lessons: Curriculum,
    ) -> None:
        """레슨 생성 성공 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        from app.modules.curriculum.application.dto.curriculum_dto import (
            CreateLessonCommand,
        )

        command = CreateLessonCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            week_number=1,
            lesson="새로운 레슨",
            lesson_index=1,
        )

        # 레슨이 추가된 새로운 WeekSchedule 생성
        updated_week_schedule = WeekSchedule(
            week_number=WeekNumber(1),
            lessons=Lessons(["기초 개념", "새로운 레슨", "환경 설정", "첫 번째 실습"]),
        )

        # 업데이트된 커리큘럼 생성
        updated_curriculum = Curriculum(  # type: ignore  # noqa: F841
            id=sample_curriculum_with_lessons.id,
            owner_id=sample_curriculum_with_lessons.owner_id,
            title=sample_curriculum_with_lessons.title,
            visibility=sample_curriculum_with_lessons.visibility,
            created_at=sample_curriculum_with_lessons.created_at,
            updated_at=sample_curriculum_with_lessons.updated_at,
            week_schedules=[updated_week_schedule],
        )

        mock_repo.find_by_id.return_value = sample_curriculum_with_lessons
        mock_repo.update.return_value = None

        # When
        result = await service.create_lesson(command, RoleVO.USER)

        # Then
        assert isinstance(result, CurriculumDTO)
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"

        mock_repo.find_by_id.assert_called_once()
        mock_repo.update.assert_called_once()

    async def test_update_lesson_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum_with_lessons: Curriculum,
    ) -> None:
        """레슨 수정 성공 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        from app.modules.curriculum.application.dto.curriculum_dto import (
            UpdateLessonCommand,
        )

        command = UpdateLessonCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            week_number=1,
            lesson_index=0,
            new_lesson="수정된 기초 개념",
        )

        mock_repo.find_by_id.return_value = sample_curriculum_with_lessons
        mock_repo.update.return_value = None

        # When
        result = await service.update_lesson(command, RoleVO.USER)  # type: ignore

        # Then
        assert isinstance(result, CurriculumDTO)
        mock_repo.find_by_id.assert_called_once()
        mock_repo.update.assert_called_once()

    async def test_delete_lesson_success(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum_with_lessons: Curriculum,
    ) -> None:
        """레슨 삭제 성공 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        from app.modules.curriculum.application.dto.curriculum_dto import (
            DeleteLessonCommand,
        )

        command = DeleteLessonCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            week_number=1,
            lesson_index=0,
        )

        mock_repo.find_by_id.return_value = sample_curriculum_with_lessons
        mock_repo.update.return_value = None

        # When
        result = await service.delete_lesson(command, RoleVO.USER)

        # Then
        assert isinstance(result, CurriculumDTO)
        mock_repo.find_by_id.assert_called_once()
        mock_repo.update.assert_called_once()

    async def test_lesson_index_out_of_range(
        self,
        curriculum_service: Tuple[CurriculumService, AsyncMock, Mock, AsyncMock, Mock],
        sample_curriculum_with_lessons: Curriculum,
    ) -> None:
        """레슨 인덱스 범위 초과 테스트"""
        # Given
        service, mock_repo, _, _, _ = curriculum_service
        from app.modules.curriculum.application.dto.curriculum_dto import (
            UpdateLessonCommand,
        )

        command = UpdateLessonCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            week_number=1,
            lesson_index=999,  # 범위 초과 인덱스
            new_lesson="수정 시도",
        )

        mock_repo.find_by_id.return_value = sample_curriculum_with_lessons

        # When & Then
        with pytest.raises(Exception):  # WeekIndexOutOfRangeError 또는 관련 예외
            await service.update_lesson(command, RoleVO.USER)  # type: ignore


class TestCreateCurriculum:
    """커리큘럼 생성 테스트"""

    @pytest.mark.asyncio
    async def test_create_curriculum_success(
        self,
        curriculum_service,  # type: ignore
        mock_curriculum_repo,  # type: ignore
        mock_curriculum_domain_service,  # type: ignore
        sample_curriculum,  # type: ignore
    ):
        """커리큘럼 생성 성공 테스트"""
        # Given
        command = CreateCurriculumCommand(
            owner_id="user_123",
            title="테스트 커리큘럼",
            week_schedules=[
                (1, ["기초 개념", "환경 설정"]),
                (2, ["심화 학습", "실습"]),
            ],
            visibility=Visibility.PRIVATE,
        )

        mock_curriculum_repo.count_by_owner.return_value = 5  # type: ignore
        mock_curriculum_domain_service.create_curriculum.return_value = (  # type: ignore
            sample_curriculum
        )
        mock_curriculum_repo.save.return_value = None  # type: ignore

        # When
        result = await curriculum_service.create_curriculum(command)  # type: ignore

        # Then
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"  # type: ignore
        assert result.title == "테스트 커리큘럼"  # type: ignore
        assert result.visibility == "PRIVATE"  # type: ignore
        assert len(result.week_schedules) == 2  # type: ignore

        mock_curriculum_repo.count_by_owner.assert_called_once_with("user_123")  # type: ignore
        mock_curriculum_domain_service.create_curriculum.assert_called_once()  # type: ignore
        mock_curriculum_repo.save.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_create_curriculum_count_limit_exceeded(
        self, curriculum_service, mock_curriculum_repo  # type: ignore
    ):
        """커리큘럼 개수 제한 초과 테스트"""
        # Given
        command = CreateCurriculumCommand(
            owner_id="user_123",
            title="테스트 커리큘럼",
            week_schedules=[(1, ["기초 개념"])],
        )

        mock_curriculum_repo.count_by_owner.return_value = 10  # type: ignore

        # When & Then
        with pytest.raises(CurriculumCountOverError):
            await curriculum_service.create_curriculum(command)  # type: ignore

        mock_curriculum_repo.save.assert_not_called()  # type: ignore


class TestGenerateCurriculum:
    """AI 커리큘럼 생성 테스트"""

    @pytest.mark.asyncio
    async def test_generate_curriculum_success(
        self,
        curriculum_service,  # type: ignore
        mock_curriculum_repo,  # type: ignore
        mock_curriculum_domain_service,  # type: ignore
        mock_llm_client,  # type: ignore
        sample_curriculum,  # type: ignore
    ):
        """AI 커리큘럼 생성 성공 테스트"""
        # Given
        command = GenerateCurriculumCommand(  # type: ignore
            owner_id="user_123",
            goal="Python 기초 학습",
            period=4,
            difficulty=Difficulty.BEGINNER,
            details="프로그래밍 입문자를 위한 과정",
        )

        llm_response = {  # type: ignore
            "title": "Python 기초 커리큘럼",
            "schedule": [
                {"week_number": 1, "lessons": ["Python 소개", "개발환경 설정"]},
                {"week_number": 2, "lessons": ["변수와 자료형", "조건문"]},
                {"week_number": 3, "lessons": ["반복문", "함수"]},
                {"week_number": 4, "lessons": ["클래스", "모듈과 패키지"]},
            ],
        }

        mock_curriculum_repo.count_by_owner.return_value = 5  # type: ignore
        mock_llm_client.generate_curriculum.return_value = llm_response  # type: ignore
        mock_curriculum_domain_service.create_curriculum.return_value = (  # type: ignore
            sample_curriculum
        )
        mock_curriculum_repo.save.return_value = None  # type: ignore

        # When
        with patch(  # type: ignore  # noqa: F821
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        ) as mock_datetime:  # type: ignore
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)  # type: ignore
            result = await curriculum_service.generate_curriculum(command)  # type: ignore

        # Then
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"  # type: ignore

        mock_llm_client.generate_curriculum.assert_called_once_with(  # type: ignore
            goal="Python 기초 학습",
            period=4,
            difficulty=Difficulty.BEGINNER,
            details="프로그래밍 입문자를 위한 과정",
        )
        mock_curriculum_domain_service.create_curriculum.assert_called_once()  # type: ignore
        mock_curriculum_repo.save.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_generate_curriculum_llm_error(
        self, curriculum_service, mock_curriculum_repo, mock_llm_client  # type: ignore
    ):
        """LLM 에러 처리 테스트"""
        # Given
        command = GenerateCurriculumCommand(  # type: ignore
            owner_id="user_123",
            goal="Python 학습",
            period=2,
            difficulty=Difficulty.BEGINNER,
            details="기초 과정",
        )

        mock_curriculum_repo.count_by_owner.return_value = 5  # type: ignore
        mock_llm_client.generate_curriculum.side_effect = Exception("LLM API Error")  # type: ignore

        # When & Then
        with pytest.raises(LLMGenerationError):
            await curriculum_service.generate_curriculum(command)  # type: ignore

    @pytest.mark.asyncio
    async def test_generate_curriculum_invalid_response(
        self, curriculum_service, mock_curriculum_repo, mock_llm_client  # type: ignore
    ):
        """잘못된 LLM 응답 처리 테스트"""
        # Given
        command = GenerateCurriculumCommand(
            owner_id="user_123",
            goal="Python 학습",
            period=2,
            difficulty=Difficulty.BEGINNER,
            details="기초 과정",
        )

        mock_curriculum_repo.count_by_owner.return_value = 5  # type: ignore
        mock_llm_client.generate_curriculum.return_value = {"invalid": "response"}  # type: ignore

        # When & Then
        with pytest.raises(LLMGenerationError):
            await curriculum_service.generate_curriculum(command)  # type: ignore


class TestGetCurriculums:
    """커리큘럼 조회 테스트"""

    @pytest.mark.asyncio
    async def test_get_curriculums_by_owner(
        self, curriculum_service, mock_curriculum_repo, sample_curriculum  # type: ignore
    ):
        """소유자별 커리큘럼 조회 테스트"""
        # Given
        query = CurriculumQuery(owner_id="user_123", page=1, items_per_page=10)  # type: ignore
        mock_curriculum_repo.find_by_owner_id.return_value = (1, [sample_curriculum])  # type: ignore

        # When
        # result = await curriculum_service.get_curriculums(query, RoleVO.USER)  # type: ignore
        result = await curriculum_service.get_curriculums(query)  # type: ignore

        # Then
        assert result.total_count == 1  # type: ignore
        assert result.page == 1  # type: ignore
        assert len(result.curriculums) == 1  # type: ignore
        assert result.curriculums[0].id == "01HKQJQJQJQJQJQJQJQJQJ"  # type: ignore

        mock_curriculum_repo.find_by_owner_id.assert_called_once_with(  # type: ignore
            owner_id="user_123", page=1, items_per_page=10  # type: ignore
        )

    @pytest.mark.asyncio
    async def test_get_public_curriculums(
        self, curriculum_service, mock_curriculum_repo, sample_curriculum  # type: ignore
    ):
        """공개 커리큘럼 조회 테스트"""
        # Given
        query = CurriculumQuery(page=1, items_per_page=10)  # type: ignore
        mock_curriculum_repo.find_public_curriculums.return_value = (  # type: ignore
            1,
            [sample_curriculum],
        )

        # When
        # result = await curriculum_service.get_curriculums(query, RoleVO.USER)  # type: ignore
        result = await curriculum_service.get_curriculums(query)  # type: ignore

        # Then
        assert result.total_count == 1  # type: ignore
        mock_curriculum_repo.find_public_curriculums.assert_called_once_with(  # type: ignore
            page=1, items_per_page=10
        )


class TestUpdateCurriculum:
    """커리큘럼 수정 테스트"""

    @pytest.mark.asyncio
    async def test_update_curriculum_success(
        self, curriculum_service, mock_curriculum_repo, sample_curriculum  # type: ignore
    ):
        """커리큘럼 수정 성공 테스트"""
        # Given
        command = UpdateCurriculumCommand(
            curriculum_id="01HKQJQJQJQJQJQJQJQJQJ",
            owner_id="user_123",
            title="수정된 제목",
            visibility=Visibility.PUBLIC,
        )

        mock_curriculum_repo.find_by_id.return_value = sample_curriculum  # type: ignore
        mock_curriculum_repo.update.return_value = None  # type: ignore

        # When
        result = await curriculum_service.update_curriculum(command, RoleVO.USER)  # type: ignore

        # Then
        assert result.id == "01HKQJQJQJQJQJQJQJQJQJ"  # type: ignore
        mock_curriculum_repo.find_by_id.assert_called_once()  # type: ignore
        mock_curriculum_repo.update.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_update_curriculum_not_found(
        self, curriculum_service, mock_curriculum_repo  # type: ignore
    ):
        """존재하지 않는 커리큘럼 수정 테스트"""
        # Given
        command = UpdateCurriculumCommand(
            curriculum_id="nonexistent",
            owner_id="user_123",
            title="수정된 제목",
        )

        mock_curriculum_repo.find_by_id.return_value = None  # type: ignore

        # When & Then
        with pytest.raises(CurriculumNotFoundError):
            await curriculum_service.update_curriculum(command, RoleVO.USER)  # type: ignore


class TestDeleteCurriculum:
    """커리큘럼 삭제 테스트"""

    @pytest.mark.asyncio
    async def test_delete_curriculum_success(
        self, curriculum_service, mock_curriculum_repo, sample_curriculum  # type: ignore
    ):
        """커리큘럼 삭제 성공 테스트"""
        # Given
        curriculum_id = "01HKQJQJQJQJQJQJQJQJQJ"
        owner_id = "user_123"

        mock_curriculum_repo.find_by_id.return_value = sample_curriculum  # type: ignore
        mock_curriculum_repo.delete.return_value = None  # type: ignore

        # When
        await curriculum_service.delete_curriculum(curriculum_id, owner_id, RoleVO.USER)  # type: ignore

        # Then
        mock_curriculum_repo.find_by_id.assert_called_once()  # type: ignore
        mock_curriculum_repo.delete.assert_called_once_with(curriculum_id)  # type: ignore

    @pytest.mark.asyncio
    async def test_delete_curriculum_permission_denied(
        self, curriculum_service, mock_curriculum_repo, sample_curriculum  # type: ignore
    ):
        """권한 없는 삭제 시도 테스트"""
        # Given
        curriculum_id = "01HKQJQJQJQJQJQJQJQJQJ"
        owner_id = "different_user"  # 다른 사용자

        mock_curriculum_repo.find_by_id.return_value = sample_curriculum  # type: ignore

        # When & Then
        with pytest.raises(PermissionError):
            await curriculum_service.delete_curriculum(  # type: ignore
                curriculum_id, owner_id, RoleVO.USER
            )

        mock_curriculum_repo.delete.assert_not_called()  # type: ignore


class TestLLMResponseParsing:
    """LLM 응답 파싱 테스트"""

    def test_parse_valid_dict_response(self, curriculum_service):  # type: ignore
        """유효한 딕셔너리 응답 파싱 테스트"""
        # Given
        llm_response = {  # type: ignore
            "title": "Python 기초",
            "schedule": [
                {"week_number": 1, "lessons": ["변수", "연산자"]},
                {"week_number": 2, "lessons": ["조건문", "반복문"]},
            ],
        }

        with patch(  # noqa: F821
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        ) as mock_datetime:  # type: ignore
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)  # type: ignore
            mock_datetime.strftime = datetime.strftime

            # When
            result = curriculum_service._parse_llm_response(llm_response, "Python")  # type: ignore

        # Then
        assert "Python 기초" in result["title"]
        assert "240115" in result["title"]  # 타임스탬프 확인
        assert len(result["week_schedules"]) == 2
        assert result["week_schedules"][0] == (1, ["변수", "연산자"])

    def test_parse_list_response(self, curriculum_service):  # type: ignore
        """리스트 형태 응답 파싱 테스트"""
        # Given
        llm_response = [  # type: ignore
            {"week_number": 1, "lessons": ["기초"]},
            {"week_number": 2, "lessons": ["심화"]},
        ]

        with patch(  # noqa: F821
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        ) as mock_datetime:  # type: ignore
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)  # type: ignore

            # When
            result = curriculum_service._parse_llm_response(llm_response, "Test Goal")  # type: ignore

        # Then
        assert "Test Goal" in result["title"]
        assert len(result["week_schedules"]) == 2

    def test_parse_response_with_invalid_items(self, curriculum_service):  # type: ignore
        """일부 잘못된 항목이 포함된 응답 파싱 테스트"""
        # Given
        llm_response = {  # type: ignore
            "title": "Test",
            "schedule": [
                {"week_number": 1, "lessons": ["유효한 레슨"]},
                {
                    "week_number": "invalid",
                    "lessons": ["무효한 주차"],
                },  # 잘못된 주차 번호
                {"week_number": 2, "lessons": []},  # 빈 레슨 리스트
                {"week_number": 3, "lessons": ["유효한 레슨2"]},
            ],
        }

        with patch(  # noqa: F821
            "app.modules.curriculum.application.service.curriculum_service.datetime"
        ) as mock_datetime:  # type: ignore
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)  # type: ignore

            # When
            result = curriculum_service._parse_llm_response(llm_response, "Test")  # type: ignore

        # Then
        # 유효한 항목만 포함되어야 함
        assert len(result["week_schedules"]) == 2
        assert result["week_schedules"][0] == (1, ["유효한 레슨"])
        assert result["week_schedules"][1] == (3, ["유효한 레슨2"])

    def test_parse_empty_response(self, curriculum_service):  # type: ignore
        """빈 응답 처리 테스트"""
        # Given
        llm_response = {"title": "Test", "schedule": []}  # type: ignore

        # When & Then
        with pytest.raises(LLMGenerationError):
            curriculum_service._parse_llm_response(llm_response, "Test")  # type: ignore


# 통합 테스트용 픽스처
@pytest.fixture
def integration_test_setup():  # type: ignore
    """통합 테스트 설정"""
    return {  # type: ignore
        "test_user_id": "test_user_123",
        "test_curriculum_data": {
            "title": "통합 테스트 커리큘럼",
            "week_schedules": [
                (1, ["1주차 내용1", "1주차 내용2"]),
                (2, ["2주차 내용1", "2주차 내용2"]),
            ],
        },
    }


# 실행용 예제
if __name__ == "__main__":
    # pytest를 사용하여 테스트 실행
    # pytest tests/test_curriculum_service.py -v
    pass
