from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.common.monitoring.metrics import (
    initialize_metrics_collector,
    shutdown_metrics_collector,
)
from app.common.monitoring.metrics_collector import MetricsService
from app.common.cache.redis_client import redis_client
from app.common.db.database import AsyncSessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def monitoring_lifespan(app: FastAPI):
    metrics_service = None

    try:
        # Prometheus 메트릭 서버 시작 (포트 8001 사용)
        await initialize_metrics_collector(port=8001)
        logger.info("📈 Metrics collector initialized on port 8001")

        # 메트릭 서비스 시작
        async with AsyncSessionLocal() as session:
            metrics_service = MetricsService(session, redis_client, update_interval=30)
            app.state.metrics_service = metrics_service
            await metrics_service.start()
            logger.info("📊 Metrics service started")

    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {e}")

    logger.info("Monitoring system startup complete")

    yield

    # 종료 시
    logger.info("📉 Shutting down monitoring system...")

    try:
        # 메트릭 서비스 중지
        if hasattr(app.state, "metrics_service") and app.state.metrics_service:
            await app.state.metrics_service.stop()
            logger.info("Metrics service stopped")

        await shutdown_metrics_collector()
        logger.info("Metrics collector shut down")

    except Exception as e:
        logger.error(f"Error shutting down monitoring: {e}")

    logger.info("Monitoring system shutdown complete")
