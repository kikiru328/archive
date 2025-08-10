from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.modules.learning.application.exception import (
    FeedbackAccessDeniedError,
    FeedbackAlreadyExistsError,
    FeedbackNotFoundError,
    InvalidFeedbackScoreError,
    InvalidSummaryContentError,
    LLMFeedbackGenerationError,
    SummaryAccessDeniedError,
    SummaryNotFoundError,
)


async def summary_not_found_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, SummaryNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    raise exc


async def summary_access_denied_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, SummaryAccessDeniedError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def invalid_summary_content_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, InvalidSummaryContentError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def feedback_not_found_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, FeedbackNotFoundError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def feedback_already_exists_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, FeedbackAlreadyExistsError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def feedback_access_denied_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, FeedbackAccessDeniedError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def invalid_feedback_score_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, InvalidFeedbackScoreError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


async def llm_feedback_generation_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, LLMFeedbackGenerationError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    raise exc


def LearningExceptionHandler(app: FastAPI):
    app.add_exception_handler(SummaryNotFoundError, summary_not_found_error)
    app.add_exception_handler(SummaryAccessDeniedError, summary_access_denied_error)
    app.add_exception_handler(InvalidSummaryContentError, invalid_summary_content_error)
    app.add_exception_handler(FeedbackNotFoundError, feedback_not_found_error)
    app.add_exception_handler(FeedbackAlreadyExistsError, feedback_already_exists_error)
    app.add_exception_handler(FeedbackAccessDeniedError, feedback_access_denied_error)
    app.add_exception_handler(InvalidFeedbackScoreError, invalid_feedback_score_error)
    app.add_exception_handler(LLMFeedbackGenerationError, llm_feedback_generation_error)
