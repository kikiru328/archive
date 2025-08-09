from fastapi import FastAPI

from app.exception_handlers.curriculum_exception_handler import (
    CurriculumExceptionHandler,
)
from app.exception_handlers.default_exception_handler import DefaultExceptionHandler
from app.exception_handlers.feed_exception_handler import FeedExceptionHandler
from app.exception_handlers.learning_exception_handelr import LearningExceptionHandler
from app.exception_handlers.social_exception_handler import SocialExceptionHandler
from app.exception_handlers.taxonomy_exception_handler import TaxonomyExceptionHandler
from app.exception_handlers.user_exception_handler import UserExceptionHandler


def setup_exception_handlers(app: FastAPI):
    DefaultExceptionHandler(app)
    CurriculumExceptionHandler(app)
    FeedExceptionHandler(app)
    LearningExceptionHandler(app)
    SocialExceptionHandler(app)
    TaxonomyExceptionHandler(app)
    UserExceptionHandler(app)
