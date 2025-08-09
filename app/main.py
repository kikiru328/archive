from fastapi import FastAPI
from app.api.v1.router import v1_router
from app.core.di_container import Container
from app.lifespan import combined_lifespan
from app.common.middleware.activity_middleware import ActivityTrackingMiddleware


class App(FastAPI):
    container: Container


app = App(
    lifespan=combined_lifespan,
    title="Curriculum Learning Platform API",
    description="A comprehensive learning platform with social features",
    version="1.0.0",
)

app.container = Container()

# 미들웨어 추가
app.add_middleware(ActivityTrackingMiddleware)

# 라우터 추가
app.include_router(v1_router)


@app.get("/")
def hello() -> dict[str, str]:
    return {
        "message": "Curriculum Learning Platform API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/metrics")
async def metrics():
    """Prometheus 메트릭 엔드포인트"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi import Response

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "curriculum-api"}
