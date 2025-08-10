from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def core_lifespan(app: FastAPI):
    logger.info("⚙️ Wire DI")
    app.container.wire()  # type: ignore # app.container 사용
    yield
    logger.info("⚙️ DI unwired")
    app.container.unwire()  # type: ignore # app.container 사용
    yield
