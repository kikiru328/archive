from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.common.cache.redis_client import redis_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def redis_lifespan(app: FastAPI):
    logger.info("🔴 Connecting Redis")
    await redis_client.connect()
    yield
    logger.info("🔴 Disconnecting Redis")
    await redis_client.disconnect()
