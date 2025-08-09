from contextlib import asynccontextmanager, AsyncExitStack
from fastapi import FastAPI

from app.lifespan.core import core_lifespan
from app.lifespan.monitoring import monitoring_lifespan
from .redis import redis_lifespan

# from .core import core_lifespan


@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        # 초기화 순서가 중요하면 원하는 순서대로 등록
        await stack.enter_async_context(monitoring_lifespan(app))
        await stack.enter_async_context(core_lifespan(app))
        await stack.enter_async_context(redis_lifespan(app))  # type: ignore
        yield  # ───── 애플리케이션 구동 중 ─────

    # ExitStack이 역순으로 안전하게 정리
