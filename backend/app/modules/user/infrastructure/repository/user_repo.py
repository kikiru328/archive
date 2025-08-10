from typing import Optional, Sequence, Tuple

from sqlalchemy import Result, Select, func, select
from app.modules.user.application.exception import UserNotFoundError
from app.modules.user.domain.entity.user import User as UserDomain
from app.modules.user.domain.repository.user_repo import IUserRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.domain.vo import Email, Name, Password, RoleVO
from app.modules.user.infrastructure.db_model.user import UserModel


class UserRepository(IUserRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _to_domain(self, user_model: UserModel) -> UserDomain:
        """DB Model → Domain Entity"""
        return UserDomain(
            id=user_model.id,
            email=Email(user_model.email),
            name=Name(user_model.name),
            password=Password(user_model.password),
            role=RoleVO(user_model.role),
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
        )

    async def save(self, user: UserDomain) -> None:
        new_user = UserModel(  # type: ignore
            id=user.id,
            email=str(user.email),
            name=str(user.name),
            password=user.password.value,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(new_user)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def find_by_id(self, id: str) -> Optional[UserDomain]:
        user: UserModel | None = await self.session.get(UserModel, id)
        if not user:
            return None
        return self._to_domain(user)

    async def find_by_email(self, email: Email) -> Optional[UserDomain]:
        query: Select[Tuple[UserModel]] = select(UserModel).where(
            UserModel.email == str(email)
        )
        response: Result[Tuple[UserModel]] = await self.session.execute(query)
        user: UserModel | None = response.scalars().first()

        if not user:
            return None
        return self._to_domain(user)

    async def find_by_name(self, name: Name) -> Optional[UserDomain]:
        query: Select[Tuple[UserModel]] = select(UserModel).where(
            UserModel.name == str(name)
        )
        response: Result[Tuple[UserModel]] = await self.session.execute(query)
        user: UserModel | None = response.scalars().first()

        if not user:
            return None
        return self._to_domain(user)

    async def find_users(
        self,
        page: int = 1,
        items_per_page: int = 10,
    ) -> tuple[int, list[UserDomain]]:
        # total count
        count_query: Select[Tuple[int]] = select(func.count()).select_from(UserModel)
        count_result: Result[Tuple[int]] = await self.session.execute(count_query)
        total_count: int = count_result.scalar_one()

        # paging
        offset: int = (page - 1) * items_per_page
        query: Select[Tuple[UserModel]] = (
            select(UserModel).offset(offset).limit(items_per_page)
        )
        result: Result[Tuple[UserModel]] = await self.session.execute(query)
        user_models: Sequence[UserModel] = result.scalars().all()

        users = [self._to_domain(user_model) for user_model in user_models]
        return (total_count, users)

    async def update(self, user: UserDomain) -> None:
        existing_user: UserModel | None = await self.session.get(UserModel, user.id)

        if not existing_user:
            raise UserNotFoundError(f"user with id={user.id} not found")

        existing_user.name = str(user.name)
        existing_user.password = user.password.value
        existing_user.role = user.role
        existing_user.updated_at = user.updated_at

        self.session.add(existing_user)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def delete(self, id: str) -> None:
        existing_user: UserModel | None = await self.session.get(UserModel, id)
        if not existing_user:
            raise UserNotFoundError(f"user with id={id} not found")

        await self.session.delete(existing_user)
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def exists_by_email(self, email: Email) -> bool:
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.email == str(email))
        )
        result: Result[Tuple[int]] = await self.session.execute(query)
        count: int = result.scalar_one()
        return count > 0

    async def exists_by_name(self, name: Name) -> bool:
        query: Select[Tuple[int]] = (
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.name == str(name))
        )
        result: Result[Tuple[int]] = await self.session.execute(query)
        count: int = result.scalar_one()
        return count > 0
