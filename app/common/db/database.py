from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # type: ignore
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import declarative_base

# from sqlalchemy.orm import sessionmaker
from app.core.config import Settings
from app.core.config import get_settings


settings: Settings = get_settings()

SQLALCHEMY_DATABASE_URL: str = settings.sqlalchemy_database_url

engine: AsyncEngine = create_async_engine(
    settings.sqlalchemy_database_url,
    echo=True,
    future=True,
    connect_args={"charset": "utf8mb4"},
)

AsyncSessionLocal = async_sessionmaker(  # type: ignore
    bind=engine,
    expire_on_commit=False,
)


Base = declarative_base()
