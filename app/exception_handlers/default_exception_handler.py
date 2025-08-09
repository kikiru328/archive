from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors()},
        )
    raise exc


async def value_error_handler(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    raise exc


def DefaultExceptionHandler(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
