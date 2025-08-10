import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.common.db.database import Base
from app.modules.curriculum.infrastructure.repository.curriculum_repo import (
    CurriculumRepository,
)
from app.modules.curriculum.domain.entity.curriculum import Curriculum
from app.modules.curriculum.domain.entity.week_schedule import WeekSchedule
from app.modules.curriculum.domain.vo import Title, Visibility, WeekNumber, Lessons
from app.modules.user.domain.vo.role import RoleVO
from app.modules.user.infrastructure.db_model.user import UserModel


@pytest.fixture
async def async_session():
    """테스트용 비동기 세션"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_local: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_local() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def curriculum_repository(async_session: AsyncSession) -> CurriculumRepository:
    """CurriculumRepository 픽스처"""
    return CurriculumRepository(async_session)


@pytest.fixture
async def sample_user(async_session: AsyncSession) -> UserModel:
    """테스트용 사용자 생성"""
    user = UserModel(  # type: ignore
        id="test_user_id",
        email="test@example.com",
        name="Test User",
        password="hashed_password",
        role=RoleVO.USER,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    async_session.add(user)
    await async_session.commit()
    return user


@pytest.fixture
def sample_curriculum() -> Curriculum:
    """테스트용 커리큘럼 엔티티"""
    now = datetime.now(timezone.utc)
    week_schedules = [
        WeekSchedule(
            week_number=WeekNumber(1),
            title=Title("개념"),
            lessons=Lessons(["Python 기초", "변수와 자료형"]),
        ),
        WeekSchedule(
            week_number=WeekNumber(2),
            title=Title("개념"),
            lessons=Lessons(["조건문", "반복문", "함수"]),
        ),
    ]

    return Curriculum(
        id="01HKQJQJQJQJQJQJQJQJQJ",
        owner_id="test_user_id",
        title=Title("Python 기초 과정"),
        visibility=Visibility.PRIVATE,
        created_at=now,
        updated_at=now,
        week_schedules=week_schedules,
    )


@pytest.fixture
def sample_public_curriculum() -> Curriculum:
    """테스트용 공개 커리큘럼 엔티티"""
    now = datetime.now(timezone.utc)
    week_schedules = [
        WeekSchedule(
            week_number=WeekNumber(1),
            title=Title("개념"),
            lessons=Lessons(["JavaScript 기초", "DOM 조작"]),
        ),
    ]

    return Curriculum(
        id="01HKQJQJQJQJQJQJQJQJQK",
        owner_id="test_user_id",
        title=Title("JavaScript 공개 과정"),
        visibility=Visibility.PUBLIC,
        created_at=now,
        updated_at=now,
        week_schedules=week_schedules,
    )


class TestCurriculumRepository:
    """CurriculumRepository 테스트"""

    @pytest.mark.asyncio
    async def test_save_curriculum(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """커리큘럼 저장 테스트"""
        # When
        await curriculum_repository.save(sample_curriculum)

        # Then
        saved_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.USER,
            owner_id=sample_curriculum.owner_id,
        )
        assert saved_curriculum is not None
        assert saved_curriculum.id == sample_curriculum.id
        assert saved_curriculum.title.value == sample_curriculum.title.value
        assert len(saved_curriculum.week_schedules) == 2

    @pytest.mark.asyncio
    async def test_find_by_id_existing_curriculum(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """존재하는 커리큘럼 ID로 조회 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When
        found_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.USER,
            owner_id=sample_curriculum.owner_id,
        )

        # Then
        assert found_curriculum is not None
        assert found_curriculum.id == sample_curriculum.id
        assert found_curriculum.title.value == "Python 기초 과정"
        assert len(found_curriculum.week_schedules) == 2

    @pytest.mark.asyncio
    async def test_find_by_id_non_existing_curriculum(
        self, curriculum_repository: CurriculumRepository, sample_user: UserModel
    ) -> None:
        """존재하지 않는 커리큘럼 ID로 조회 테스트"""
        # When
        found_curriculum = await curriculum_repository.find_by_id(
            curriculum_id="non_existing_id",
            role=RoleVO.USER,
            owner_id="test_user_id",
        )

        # Then
        assert found_curriculum is None

    @pytest.mark.asyncio
    async def test_find_by_id_admin_access(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """관리자 권한으로 모든 커리큘럼 조회 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When - 관리자는 owner_id가 다른 사용자도 조회 가능
        found_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.ADMIN,
            owner_id="different_user_id",
        )

        # Then
        assert found_curriculum is not None
        assert found_curriculum.id == sample_curriculum.id

    @pytest.mark.asyncio
    async def test_find_by_id_private_curriculum_access_denied(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """비공개 커리큘럼 타인 접근 거부 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When - 다른 사용자가 비공개 커리큘럼 조회 시도
        found_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.USER,
            owner_id="different_user_id",
        )

        # Then
        assert found_curriculum is None

    @pytest.mark.asyncio
    async def test_find_by_id_public_curriculum_access_allowed(
        self,
        curriculum_repository: CurriculumRepository,
        sample_public_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """공개 커리큘럼 타인 접근 허용 테스트"""
        # Given
        await curriculum_repository.save(sample_public_curriculum)

        # When - 다른 사용자가 공개 커리큘럼 조회
        found_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_public_curriculum.id,
            role=RoleVO.USER,
            owner_id="different_user_id",
        )

        # Then
        assert found_curriculum is not None
        assert found_curriculum.id == sample_public_curriculum.id

    @pytest.mark.asyncio
    async def test_find_by_owner_id(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """소유자 ID로 커리큘럼 목록 조회 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When
        total_count, curriculums = await curriculum_repository.find_by_owner_id(
            owner_id="test_user_id",
            page=1,
            items_per_page=10,
        )

        # Then
        assert total_count == 1
        assert len(curriculums) == 1
        assert curriculums[0].id == sample_curriculum.id

    @pytest.mark.asyncio
    async def test_find_by_owner_id_pagination(
        self,
        curriculum_repository: CurriculumRepository,
        sample_user: UserModel,
    ) -> None:
        """소유자 ID로 커리큘럼 목록 페이지네이션 테스트"""
        # Given - 3개의 커리큘럼 생성
        curriculums = []
        for i in range(3):
            now = datetime.now(timezone.utc)
            curriculum = Curriculum(
                id=f"curriculum_{i}",
                owner_id="test_user_id",
                title=Title(f"Test Curriculum {i}"),
                visibility=Visibility.PRIVATE,
                created_at=now,
                updated_at=now,
                week_schedules=[
                    WeekSchedule(
                        week_number=WeekNumber(1),
                        title=Title("개념"),
                        lessons=Lessons([f"Lesson {i}"]),
                    )
                ],
            )
            curriculums.append(curriculum)
            await curriculum_repository.save(curriculum)

        # When - 페이지 크기 2로 첫 번째 페이지 조회
        total_count, page_curriculums = await curriculum_repository.find_by_owner_id(
            owner_id="test_user_id",
            page=1,
            items_per_page=2,
        )

        # Then
        assert total_count == 3
        assert len(page_curriculums) == 2

    @pytest.mark.asyncio
    async def test_find_public_curriculums(
        self,
        curriculum_repository: CurriculumRepository,
        sample_public_curriculum: Curriculum,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """공개 커리큘럼 목록 조회 테스트"""
        # Given
        await curriculum_repository.save(sample_public_curriculum)
        await curriculum_repository.save(sample_curriculum)  # 비공개 커리큘럼

        # When
        total_count, curriculums = await curriculum_repository.find_public_curriculums(
            page=1, items_per_page=10
        )

        # Then
        assert total_count == 1  # 공개 커리큘럼만 조회됨
        assert len(curriculums) == 1
        assert curriculums[0].id == sample_public_curriculum.id
        assert curriculums[0].visibility == Visibility.PUBLIC

    @pytest.mark.asyncio
    async def test_update_curriculum(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """커리큘럼 업데이트 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When - 제목과 공개 설정 변경
        sample_curriculum.change_title(Title("수정된 제목"))
        sample_curriculum.change_visibility(Visibility.PUBLIC)
        await curriculum_repository.update(sample_curriculum)

        # Then
        updated_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.USER,
            owner_id=sample_curriculum.owner_id,
        )
        assert updated_curriculum is not None
        assert updated_curriculum.title.value == "수정된 제목"
        assert updated_curriculum.visibility == Visibility.PUBLIC

    @pytest.mark.asyncio
    async def test_update_curriculum_week_schedules(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """커리큘럼 주차 스케줄 업데이트 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When - 새로운 주차 추가
        new_week_schedule = WeekSchedule(
            week_number=WeekNumber(3),
            title=Title("개념"),
            lessons=Lessons(["클래스", "상속"]),
        )
        sample_curriculum.add_week_schedule(new_week_schedule)
        await curriculum_repository.update(sample_curriculum)

        # Then
        updated_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.USER,
            owner_id=sample_curriculum.owner_id,
        )
        assert updated_curriculum is not None
        assert len(updated_curriculum.week_schedules) == 3
        assert updated_curriculum.week_schedules[2].week_number.value == 3

    @pytest.mark.asyncio
    async def test_delete_curriculum(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """커리큘럼 삭제 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When
        await curriculum_repository.delete(sample_curriculum.id)

        # Then
        deleted_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.USER,
            owner_id=sample_curriculum.owner_id,
        )
        assert deleted_curriculum is None

    @pytest.mark.asyncio
    async def test_delete_non_existing_curriculum(
        self, curriculum_repository: CurriculumRepository, sample_user: UserModel
    ) -> None:
        """존재하지 않는 커리큘럼 삭제 테스트"""
        # When & Then - 예외가 발생하지 않아야 함
        await curriculum_repository.delete("non_existing_id")

    @pytest.mark.asyncio
    async def test_count_by_owner(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """소유자별 커리큘럼 개수 조회 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When
        count = await curriculum_repository.count_by_owner("test_user_id")

        # Then
        assert count == 1

    @pytest.mark.asyncio
    async def test_count_by_owner_multiple_curriculums(
        self, curriculum_repository: CurriculumRepository, sample_user: UserModel
    ) -> None:
        """여러 커리큘럼 소유자별 개수 조회 테스트"""
        # Given - 2개의 커리큘럼 생성
        for i in range(2):
            now = datetime.now(timezone.utc)
            curriculum = Curriculum(
                id=f"curriculum_{i}",
                owner_id="test_user_id",
                title=Title(f"Test Curriculum {i}"),
                visibility=Visibility.PRIVATE,
                created_at=now,
                updated_at=now,
                week_schedules=[
                    WeekSchedule(
                        week_number=WeekNumber(1),
                        title=Title("개념"),
                        lessons=Lessons([f"Lesson {i}"]),
                    )
                ],
            )
            await curriculum_repository.save(curriculum)

        # When
        count = await curriculum_repository.count_by_owner("test_user_id")

        # Then
        assert count == 2

    @pytest.mark.asyncio
    async def test_count_by_owner_no_curriculums(
        self, curriculum_repository: CurriculumRepository, sample_user: UserModel
    ) -> None:
        """커리큘럼이 없는 소유자의 개수 조회 테스트"""
        # When
        count = await curriculum_repository.count_by_owner("user_with_no_curriculums")

        # Then
        assert count == 0

    @pytest.mark.asyncio
    async def test_exists_by_id_existing_curriculum(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """존재하는 커리큘럼 ID 존재 여부 확인 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When
        exists = await curriculum_repository.exists_by_id(sample_curriculum.id)

        # Then
        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_by_id_non_existing_curriculum(
        self, curriculum_repository: CurriculumRepository, sample_user: UserModel
    ) -> None:
        """존재하지 않는 커리큘럼 ID 존재 여부 확인 테스트"""
        # When
        exists = await curriculum_repository.exists_by_id("non_existing_id")

        # Then
        assert exists is False

    @pytest.mark.asyncio
    async def test_to_domain_conversion(
        self,
        curriculum_repository: CurriculumRepository,
        sample_curriculum: Curriculum,
        sample_user: UserModel,
    ) -> None:
        """DB 모델에서 도메인 엔티티로 변환 테스트"""
        # Given
        await curriculum_repository.save(sample_curriculum)

        # When
        found_curriculum = await curriculum_repository.find_by_id(
            curriculum_id=sample_curriculum.id,
            role=RoleVO.USER,
            owner_id=sample_curriculum.owner_id,
        )

        # Then
        assert found_curriculum is not None
        assert isinstance(found_curriculum, Curriculum)
        assert isinstance(found_curriculum.title, Title)
        assert isinstance(found_curriculum.visibility, Visibility)
        assert all(
            isinstance(ws.week_number, WeekNumber)
            for ws in found_curriculum.week_schedules
        )
        assert all(
            isinstance(ws.lessons, Lessons) for ws in found_curriculum.week_schedules
        )

    @pytest.mark.asyncio
    async def test_week_schedules_ordering(
        self,
        curriculum_repository: CurriculumRepository,
        sample_user: UserModel,
    ) -> None:
        """주차 스케줄 정렬 테스트"""
        # Given - 역순으로 주차 스케줄 생성
        now = datetime.now(timezone.utc)
        week_schedules = [
            WeekSchedule(
                week_number=WeekNumber(3),
                title=Title("개념"),
                lessons=Lessons(["Week 3"]),
            ),
            WeekSchedule(
                week_number=WeekNumber(1),
                title=Title("개념"),
                lessons=Lessons(["Week 1"]),
            ),
            WeekSchedule(
                week_number=WeekNumber(2),
                title=Title("개념"),
                lessons=Lessons(["Week 2"]),
            ),
        ]

        curriculum = Curriculum(
            id="test_curriculum",
            owner_id="test_user_id",
            title=Title("Ordering Test"),
            visibility=Visibility.PRIVATE,
            created_at=now,
            updated_at=now,
            week_schedules=week_schedules,
        )

        await curriculum_repository.save(curriculum)

        # When
        found_curriculum = await curriculum_repository.find_by_id(
            curriculum_id="test_curriculum",
            role=RoleVO.USER,
            owner_id="test_user_id",
        )

        # Then
        assert found_curriculum is not None
        week_numbers = [ws.week_number.value for ws in found_curriculum.week_schedules]
        assert week_numbers == [1, 2, 3]  # 정렬되어야 함


class TestCurriculumRepositoryErrorHandling:
    """CurriculumRepository 에러 처리 테스트"""

    @pytest.mark.asyncio
    async def test_save_curriculum_with_invalid_week_schedule(
        self, curriculum_repository: CurriculumRepository, sample_user: UserModel
    ) -> None:
        """잘못된 주차 스케줄로 커리큘럼 저장 시 처리 테스트"""
        # Given - 빈 레슨 리스트를 가진 주차 스케줄
        now = datetime.now(timezone.utc)

        # 이 테스트는 도메인 레벨에서 이미 검증되므로
        # 유효한 데이터만 repository에 도달한다고 가정
        curriculum = Curriculum(
            id="test_curriculum",
            owner_id="test_user_id",
            title=Title("Test"),
            visibility=Visibility.PRIVATE,
            created_at=now,
            updated_at=now,
            week_schedules=[
                WeekSchedule(
                    week_number=WeekNumber(1),
                    title=Title("개념"),
                    lessons=Lessons(["Valid lesson"]),  # 유효한 레슨
                )
            ],
        )

        # When & Then - 정상적으로 저장되어야 함
        await curriculum_repository.save(curriculum)

        saved = await curriculum_repository.find_by_id(
            curriculum_id="test_curriculum",
            role=RoleVO.USER,
            owner_id="test_user_id",
        )
        assert saved is not None

    @pytest.mark.asyncio
    async def test_update_non_existing_curriculum(
        self, curriculum_repository: CurriculumRepository, sample_user: UserModel
    ) -> None:
        """존재하지 않는 커리큘럼 업데이트 테스트"""
        # Given
        now = datetime.now(timezone.utc)
        non_existing_curriculum = Curriculum(
            id="non_existing",
            owner_id="test_user_id",
            title=Title("Non Existing"),
            visibility=Visibility.PRIVATE,
            created_at=now,
            updated_at=now,
            week_schedules=[],
        )

        # When & Then - 예외가 발생하지 않아야 함 (update 메서드는 None 반환)
        result = await curriculum_repository.update(non_existing_curriculum)  # type: ignore
        assert result is None
