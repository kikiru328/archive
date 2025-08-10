from fastapi import FastAPI
from app.api.v1.router import v1_router
from app.core.default_router import default_router
from app.core.di_container import Container
from app.exception_handlers import setup_exception_handlers
from app.lifespan import combined_lifespan
from app.common.middleware.activity_middleware import ActivityTrackingMiddleware
from fastapi.middleware.cors import CORSMiddleware


class App(FastAPI):
    container: Container


app = App(
    lifespan=combined_lifespan,
    title="Curriculum Learning Platform API",
    description="A comprehensive learning platform with social features",
    version="1.0.0",
)

app.container = Container()

setup_exception_handlers(app)

# 미들웨어 추가
app.add_middleware(ActivityTrackingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(v1_router)
app.include_router(default_router)
