from fastapi import APIRouter


default_router = APIRouter(prefix="")


@default_router.get("/", tags=["Default"])
def hello() -> dict[str, str]:
    return {
        "message": "Curriculum Learning Platform API",
        "version": "1.0.0",
        "status": "running",
    }


@default_router.get("/metrics", tags=["Default"])
async def metrics():
    """Prometheus 메트릭 엔드포인트"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi import Response

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@default_router.get("/health", tags=["Default"])
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "curriculum-api"}
