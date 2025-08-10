from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.modules.taxonomy.application.exception import (
    CategoryAccessDeniedError,
    CategoryInUseError,
    CategoryNotFoundError,
    DuplicateCategoryError,
    DuplicateTagError,
    InactiveCategoryAssignmentError,
    InvalidCategoryNameError,
    InvalidColorFormatError,
    InvalidTagNameError,
    TagAccessDeniedError,
    TagInUseError,
    TagLimitExceededError,
    TagNotFoundError,
)


async def tag_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, TagNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def category_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, CategoryNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def duplicate_tag_error(request: Request, exc: Exception):
    if isinstance(exc, DuplicateTagError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def duplicate_category_error(request: Request, exc: Exception):
    if isinstance(exc, DuplicateCategoryError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def tag_access_denied_error(request: Request, exc: Exception):
    if isinstance(exc, TagAccessDeniedError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    raise exc


async def category_access_denied_error(request: Request, exc: Exception):
    if isinstance(exc, CategoryAccessDeniedError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    raise exc


async def invalid_tag_name_error(request: Request, exc: Exception):
    if isinstance(exc, InvalidTagNameError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def invalid_category_name_error(request: Request, exc: Exception):
    if isinstance(exc, InvalidCategoryNameError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def invalid_color_format_error(request: Request, exc: Exception):
    if isinstance(exc, InvalidColorFormatError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def category_in_use_error(request: Request, exc: Exception):
    if isinstance(exc, CategoryInUseError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def tag_in_use_error(request: Request, exc: Exception):
    if isinstance(exc, TagInUseError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def tag_limit_exceeded_error(request: Request, exc: Exception):
    if isinstance(exc, TagLimitExceededError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def inactive_category_assignment_error(request: Request, exc: Exception):
    if isinstance(exc, InactiveCategoryAssignmentError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


def TaxonomyExceptionHandler(app: FastAPI):
    # 404 Not Found
    app.add_exception_handler(TagNotFoundError, tag_not_found_error)
    app.add_exception_handler(CategoryNotFoundError, category_not_found_error)

    # 409 Conflict
    app.add_exception_handler(DuplicateTagError, duplicate_tag_error)
    app.add_exception_handler(DuplicateCategoryError, duplicate_category_error)
    app.add_exception_handler(CategoryInUseError, category_in_use_error)
    app.add_exception_handler(TagInUseError, tag_in_use_error)

    # 403 Forbidden
    app.add_exception_handler(TagAccessDeniedError, tag_access_denied_error)
    app.add_exception_handler(CategoryAccessDeniedError, category_access_denied_error)

    # 400 Bad Request
    app.add_exception_handler(InvalidTagNameError, invalid_tag_name_error)
    app.add_exception_handler(InvalidCategoryNameError, invalid_category_name_error)
    app.add_exception_handler(InvalidColorFormatError, invalid_color_format_error)
    app.add_exception_handler(TagLimitExceededError, tag_limit_exceeded_error)
    app.add_exception_handler(
        InactiveCategoryAssignmentError, inactive_category_assignment_error
    )
