from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.modules.feed.application.exception import FeedCacheError, FeedNotFoundError


async def feed_not_found_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, FeedNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )
    raise exc


async def feed_cache_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, FeedCacheError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    raise exc


def FeedExceptionHandler(app: FastAPI):
    app.add_exception_handler(FeedNotFoundError, feed_not_found_error)
    app.add_exception_handler(FeedCacheError, feed_cache_error)
