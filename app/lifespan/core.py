# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from app.core.di_container import Container
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def core_lifespan(app: FastAPI):
#     logger.info("⚙️  Wire DI")
#     app.container: Container # type: ignore
#     app.container.wire(
#         packages=[
#             "user.interface.controllers",
#             "curriculum.interface.controllers",
#             "admin.interface.controllers",
#             "monitoring",
#         ]
#     )
#     yield
#     logger.info("⚙️  DI unwired (nothing to clean)")
