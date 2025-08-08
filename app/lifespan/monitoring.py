# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from app.metrics import initialize_metrics_collector, shutdown_metrics_collector
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def monitoring_lifespan(app: FastAPI):
#     try:
#         await initialize_metrics_collector()
#         logger.info("📈 Metrics collector initialized")
#     except Exception as e:
#         logger.error(f"Failed to initialize metrics collector: {e}")

#     logger.info("Application startup complete")

#     yield

#     # 종료 시
#     logger.info("📉Shutting down application...")

#     # 메트릭 컬렉터 종료
#     try:
#         await shutdown_metrics_collector()
#         logger.info("Metrics collector shut down")
#     except Exception as e:
#         logger.error(f"Error shutting down metrics collector: {e}")

#     logger.info("Application shutdown complete")
