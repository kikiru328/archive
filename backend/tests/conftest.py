"""
pytest 공통 설정 및 fixture 정의
"""

from datetime import datetime, timezone
from typing import Any, Generator
import pytest
from ulid import ULID  # type: ignore
from freezegun import freeze_time
import asyncio
from unittest.mock import AsyncMock, Mock
from pytest_mock import MockerFixture
from app.modules.curriculum.application.service.curriculum_service import (
    CurriculumService,
)
from app.modules.curriculum.domain.repository.curriculum_repo import (
    ICurriculumRepository,
)
from app.modules.curriculum.domain.service.curriculum_domain_service import (
    CurriculumDomainService,
)
from app.common.llm.llm_client_repo import ILLMClientRepository
from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.vo import Title, Visibility, WeekNumber, Lessons
from app.modules.social.domain.repository.follow_repo import IFollowRepository


@pytest.fixture(autouse=True)  # type: ignore
def _freeze_time() -> Generator[None, Any, None]:  # type: ignore
    """모든 테스트에서 시간 고정"""
    with freeze_time("2025-08-04T15:00:00+00:00"):
        yield


@pytest.fixture(scope="session")  # type: ignore
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 통합 테스트용 설정 (필요시 사용)
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


@pytest.fixture
def mock_curriculum_repo(mocker: MockerFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=ICurriculumRepository)


@pytest.fixture
def mock_curriculum_domain_service(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=CurriculumDomainService)


@pytest.fixture
def mock_llm_client(mocker: MockerFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=ILLMClientRepository)


@pytest.fixture
def mock_follow_repo(mocker: MockerFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=IFollowRepository)


@pytest.fixture
def mock_ulid(mocker: MockerFixture) -> Mock:
    ulid = mocker.Mock(spec=ULID)
    ulid.generate.return_value = "01HKQJQJQJQJQJQJQJQJQJ"
    return ulid


@pytest.fixture
def curriculum_service(
    mock_curriculum_repo: AsyncMock,
    mock_curriculum_domain_service: Mock,
    mock_llm_client: AsyncMock,
    mock_follow_repo: AsyncMock,
    mock_ulid: Mock,
) -> CurriculumService:
    """테스트 대상 CurriculumService 인스턴스"""
    service = CurriculumService(
        curriculum_repo=mock_curriculum_repo,
        curriculum_domain_service=mock_curriculum_domain_service,
        llm_client=mock_llm_client,
        follow_repo=mock_follow_repo,
        ulid=mock_ulid,
    )
    return service


@pytest.fixture
def sample_curriculum() -> Curriculum:
    now = datetime.now(timezone.utc)
    schedules = [
        WeekSchedule(
            week_number=WeekNumber(1), lessons=Lessons(["기초 개념", "환경 설정"])
        ),
        WeekSchedule(week_number=WeekNumber(2), lessons=Lessons(["심화 학습", "실습"])),
    ]
    return Curriculum(
        id="01HKQJQJQJQJQJQJQJQJQJ",
        owner_id="user_123",
        title=Title("테스트 커리큘럼"),
        visibility=Visibility.PRIVATE,
        created_at=now,
        updated_at=now,
        week_schedules=schedules,
    )
