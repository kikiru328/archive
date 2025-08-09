from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.modules.user.application.exception import (
    EmailNotFoundError,
    ExistEmailError,
    ExistNameError,
    PasswordIncorrectError,
    UserNotFoundError,
)


async def user_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, UserNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def exist_name_error(request: Request, exc: Exception):
    if isinstance(exc, ExistNameError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def exist_email_error(request: Request, exc: Exception):
    if isinstance(exc, ExistEmailError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def email_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, EmailNotFoundError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})
    raise exc


async def password_incorrect_error(request: Request, exc: Exception):
    if isinstance(exc, PasswordIncorrectError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})
    raise exc


def UserExceptionHandler(app: FastAPI):
    # 404 Not Found
    app.add_exception_handler(UserNotFoundError, user_not_found_error)

    # 409 Conflict
    app.add_exception_handler(ExistNameError, exist_name_error)
    app.add_exception_handler(ExistEmailError, exist_email_error)

    # 401 Unauthorized
    app.add_exception_handler(EmailNotFoundError, email_not_found_error)
    app.add_exception_handler(PasswordIncorrectError, password_incorrect_error)
