# app/common/db/session.py
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator  # ✅ Python 3.9+ 권장
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.db.database import AsyncSessionLocal


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """
    FastAPI 요청마다 호출되어
    - 세션을 열고 (`async with AsyncSessionLocal()`)
    - 호출 측에 넘겨주고 (`yield session`)
    - 블록이 끝나면 자동으로 세션을 닫아 풀에 반납합니다.
    """
    async with AsyncSessionLocal() as session:
        yield session  # `async with` 블록이 close()를 책임
