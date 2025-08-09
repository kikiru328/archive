from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.common.monitoring.metrics import (
    initialize_metrics_collector,
    shutdown_metrics_collector,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def monitoring_lifespan(app: FastAPI):
    try:
        # Prometheus 메트릭 서버 시작
        await initialize_metrics_collector(port=8000)
        logger.info("📈 Metrics collector initialized on port 8000")
    except Exception as e:
        logger.error(f"Failed to initialize metrics collector: {e}")

    logger.info("Monitoring system startup complete")

    yield

    # 종료 시
    logger.info("📉 Shutting down monitoring system...")

    try:
        await shutdown_metrics_collector()
        logger.info("Metrics collector shut down")
    except Exception as e:
        logger.error(f"Error shutting down metrics collector: {e}")

    logger.info("Monitoring system shutdown complete")
