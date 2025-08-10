from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.modules.curriculum.application.exception import (
    CurriculumAccessDeniedError,
    CurriculumCountOverError,
    CurriculumNotFoundError,
    InvalidCurriculumStructureError,
    InvalidLLMResponseError,
    LLMGenerationError,
    WeekIndexOutOfRangeError,
    WeekScheduleNotFoundError,
)


async def curriculum_not_found_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, CurriculumNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )
    raise exc


async def curriculum_count_over_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, CurriculumCountOverError):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )
    raise exc


async def weekschedule_not_found_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, WeekScheduleNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )
    raise exc


async def week_index_out_of_range_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, WeekIndexOutOfRangeError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    raise exc


async def invalid_curriculum_structure_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, InvalidCurriculumStructureError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    raise exc


async def curriculum_access_denied_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, CurriculumAccessDeniedError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    raise exc


async def llm_generation_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, LLMGenerationError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    raise exc


async def invalid_llm_reponse_error(
    request: Request,
    exc: Exception,
):
    if isinstance(exc, InvalidLLMResponseError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    raise exc


def CurriculumExceptionHandler(app: FastAPI):
    app.add_exception_handler(CurriculumNotFoundError, curriculum_not_found_error)
    app.add_exception_handler(CurriculumCountOverError, curriculum_count_over_error)
    app.add_exception_handler(WeekScheduleNotFoundError, weekschedule_not_found_error)
    app.add_exception_handler(WeekIndexOutOfRangeError, week_index_out_of_range_error)
    app.add_exception_handler(
        InvalidCurriculumStructureError, invalid_curriculum_structure_error
    )
    app.add_exception_handler(
        CurriculumAccessDeniedError, curriculum_access_denied_error
    )
    app.add_exception_handler(LLMGenerationError, llm_generation_error)
    app.add_exception_handler(InvalidLLMResponseError, invalid_llm_reponse_error)
