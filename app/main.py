from fastapi import FastAPI
from app.api.v1.router import v1_router
from app.core.di_container import Container
from app.lifespan import combined_lifespan


class App(FastAPI):
    container: Container


app = App(
    lifespan=combined_lifespan,
    title="Curriculum Learning Platform API",
    description="A comprehensive learning platform with social features",
    version="1.0.0",
)

app.container = Container()
app.include_router(v1_router)
# app.include_router(monitoring_router)
# app.middleware(PrometheusMiddleware)
# app.middleware(HealthCheckMiddleware)
# exception_handlers(app)


@app.get("/")
def hello() -> dict[str, str]:
    return {
        "message": "Curriculum Learning Platform API",
        "version": "1.0.0",
        "status": "running",
    }
