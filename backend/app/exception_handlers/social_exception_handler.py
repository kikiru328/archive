from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.modules.social.application.exception import (
    AlreadyFollowingError,
    BookmarkAlreadyExistsError,
    BookmarkNotFoundError,
    CommentAccessDeniedError,
    CommentNotFoundError,
    CurriculumNotAccessibleError,
    FollowAccessDeniedError,
    FollowNotFoundError,
    InvalidCommentContentError,
    LikeAlreadyExistsError,
    LikeNotFoundError,
    NotFollowingError,
    SelfFollowError,
    SocialAccessDeniedError,
)


async def like_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, LikeNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def comment_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, CommentNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def bookmark_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, BookmarkNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def follow_not_found_error(request: Request, exc: Exception):
    if isinstance(exc, FollowNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def like_already_exists_error(request: Request, exc: Exception):
    if isinstance(exc, LikeAlreadyExistsError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def bookmark_already_exists_error(request: Request, exc: Exception):
    if isinstance(exc, BookmarkAlreadyExistsError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def already_following_error(request: Request, exc: Exception):
    if isinstance(exc, AlreadyFollowingError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    raise exc


async def not_following_error(request: Request, exc: Exception):
    if isinstance(exc, NotFollowingError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def self_follow_error(request: Request, exc: Exception):
    if isinstance(exc, SelfFollowError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def social_access_denied_error(request: Request, exc: Exception):
    if isinstance(exc, SocialAccessDeniedError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    raise exc


async def comment_access_denied_error(request: Request, exc: Exception):
    if isinstance(exc, CommentAccessDeniedError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    raise exc


async def follow_access_denied_error(request: Request, exc: Exception):
    if isinstance(exc, FollowAccessDeniedError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    raise exc


async def invalid_comment_content_error(request: Request, exc: Exception):
    if isinstance(exc, InvalidCommentContentError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def curriculum_not_accessible_error(request: Request, exc: Exception):
    if isinstance(exc, CurriculumNotAccessibleError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    raise exc


def SocialExceptionHandler(app: FastAPI):
    # 404 Not Found
    app.add_exception_handler(LikeNotFoundError, like_not_found_error)
    app.add_exception_handler(CommentNotFoundError, comment_not_found_error)
    app.add_exception_handler(BookmarkNotFoundError, bookmark_not_found_error)
    app.add_exception_handler(FollowNotFoundError, follow_not_found_error)

    # 409 Conflict
    app.add_exception_handler(LikeAlreadyExistsError, like_already_exists_error)
    app.add_exception_handler(BookmarkAlreadyExistsError, bookmark_already_exists_error)
    app.add_exception_handler(AlreadyFollowingError, already_following_error)

    # 400 Bad Request
    app.add_exception_handler(NotFollowingError, not_following_error)
    app.add_exception_handler(SelfFollowError, self_follow_error)
    app.add_exception_handler(InvalidCommentContentError, invalid_comment_content_error)

    # 403 Forbidden
    app.add_exception_handler(SocialAccessDeniedError, social_access_denied_error)
    app.add_exception_handler(CommentAccessDeniedError, comment_access_denied_error)
    app.add_exception_handler(FollowAccessDeniedError, follow_access_denied_error)
    app.add_exception_handler(
        CurriculumNotAccessibleError, curriculum_not_accessible_error
    )
