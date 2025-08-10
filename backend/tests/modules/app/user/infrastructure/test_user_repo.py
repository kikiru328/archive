import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.common.db.database import Base
from app.modules.user.infrastructure.repository.user_repo import UserRepository
from app.modules.user.domain.entity.user import User
from app.modules.user.domain.vo import Email, Name, Password, RoleVO


@pytest.fixture  # type: ignore
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
def user_repository(async_session: AsyncSession) -> UserRepository:
    """UserRepository 픽스처"""
    return UserRepository(async_session)


@pytest.fixture
def sample_user():
    """테스트용 사용자 엔티티"""
    return User(
        id="01H8ABC123DEF456GHI789JKL",
        email=Email("test@example.com"),
        name=Name("testuser"),
        password=Password("hashed_password_123"),
        role=RoleVO.USER,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class TestUserRepository:
    """UserRepository 테스트"""

    @pytest.mark.asyncio
    async def test_save_user(
        self, user_repository: UserRepository, sample_user: User
    ) -> None:
        """사용자 저장 테스트"""
        # When
        await user_repository.save(sample_user)

        # Then
        saved_user = await user_repository.find_by_id(sample_user.id)
        assert saved_user is not None
        assert saved_user.id == sample_user.id
        assert saved_user.email.value == sample_user.email.value
        assert saved_user.name.value == sample_user.name.value

    @pytest.mark.asyncio
    async def test_find_by_id_existing_user(
        self, user_repository: UserRepository, sample_user: User
    ) -> None:
        """존재하는 사용자 ID로 조회 테스트"""
        # Given
        await user_repository.save(sample_user)

        # When
        found_user: User | None = await user_repository.find_by_id(sample_user.id)

        # Then
        assert found_user is not None
        assert found_user.id == sample_user.id

    @pytest.mark.asyncio
    async def test_find_by_id_non_existing_user(
        self, user_repository: UserRepository
    ) -> None:
        """존재하지 않는 사용자 ID로 조회 테스트"""
        # When
        found_user: User | None = await user_repository.find_by_id("non_existing_id")

        # Then
        assert found_user is None

    @pytest.mark.asyncio
    async def test_find_by_email_existing_user(
        self, user_repository: UserRepository, sample_user: User
    ) -> None:
        """존재하는 이메일로 조회 테스트"""
        # Given
        await user_repository.save(sample_user)

        # When
        found_user: User | None = await user_repository.find_by_email(sample_user.email)

        # Then
        assert found_user is not None
        assert found_user.email.value == sample_user.email.value

    @pytest.mark.asyncio
    async def test_find_by_email_non_existing_user(
        self, user_repository: UserRepository
    ) -> None:
        """존재하지 않는 이메일로 조회 테스트"""
        # When
        found_user: User | None = await user_repository.find_by_email(
            Email("nonexistent@example.com")
        )

        # Then
        assert found_user is None

    @pytest.mark.asyncio
    async def test_find_by_name_existing_user(
        self, user_repository: UserRepository, sample_user: User
    ):
        """존재하는 이름으로 조회 테스트"""
        # Given
        await user_repository.save(sample_user)

        # When
        found_user = await user_repository.find_by_name(sample_user.name)

        # Then
        assert found_user is not None
        assert found_user.name.value == sample_user.name.value

    @pytest.mark.asyncio
    async def test_find_by_name_non_existing_user(
        self, user_repository: UserRepository
    ):
        """존재하지 않는 이름으로 조회 테스트"""
        # When
        found_user: User | None = await user_repository.find_by_name(
            Name("nonexistent")
        )

        # Then
        assert found_user is None

    @pytest.mark.asyncio
    async def test_find_users_pagination(self, user_repository: UserRepository):
        """사용자 목록 페이지네이션 테스트"""
        # Given
        users: list[User] = [
            User(
                id=f"user_{i}",
                email=Email(f"user{i}@example.com"),
                name=Name(f"user{i}"),
                password=Password(f"password_{i}"),
                role=RoleVO.USER,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            for i in range(5)
        ]

        for user in users:
            await user_repository.save(user)

        # When
        total_count, found_users = await user_repository.find_users(
            page=1, items_per_page=3
        )

        # Then
        assert total_count == 5
        assert len(found_users) == 3

    @pytest.mark.asyncio
    async def test_update_user(
        self, user_repository: UserRepository, sample_user: User
    ) -> None:
        """사용자 정보 수정 테스트"""
        # Given
        await user_repository.save(sample_user)

        # When
        sample_user.name = Name("updated name")
        sample_user.updated_at = datetime.now(timezone.utc)
        await user_repository.update(sample_user)

        # Then
        updated_user: User | None = await user_repository.find_by_id(sample_user.id)
        assert updated_user is not None
        assert updated_user.name.value == "updated name"

    @pytest.mark.asyncio
    async def test_delete_user(
        self, user_repository: UserRepository, sample_user: User
    ) -> None:
        """사용자 삭제 테스트"""
        # Given
        await user_repository.save(sample_user)

        # When
        await user_repository.delete(sample_user.id)

        # Then
        deleted_user: User | None = await user_repository.find_by_id(sample_user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_exists_by_email(
        self, user_repository: UserRepository, sample_user: User
    ):
        """이메일 존재 여부 확인 테스트"""
        # Given
        await user_repository.save(sample_user)

        # When
        exists: bool = await user_repository.exists_by_email(sample_user.email)
        not_exists: bool = await user_repository.exists_by_email(
            Email("notexist@example.com")
        )

        # Then
        assert exists is True
        assert not_exists is False

    @pytest.mark.asyncio
    async def test_exists_by_name(
        self, user_repository: UserRepository, sample_user: User
    ) -> None:
        """이름 존재 여부 확인 테스트"""
        # Given
        await user_repository.save(sample_user)

        # When
        exists: bool = await user_repository.exists_by_name(sample_user.name)
        not_exists: bool = await user_repository.exists_by_name(Name("notexist"))

        # Then
        assert exists is True
        assert not_exists is False
