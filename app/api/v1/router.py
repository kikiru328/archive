from fastapi import APIRouter
from app.modules.user.interface.controller.user_controller import user_router
from app.modules.user.interface.controller.auth_controller import auth_router
from app.modules.curriculum.interface.controller.curriculum_controller import (
    curriculum_router,
    week_router,
    lesson_router,
)
from app.modules.learning.interface.controller.summary_controller import (
    summary_router,
    user_summary_router,
)
from app.modules.learning.interface.controller.feedback_controller import (
    feedback_router,
    # curriculum_feedback_router,
    user_feedback_router,
)
from app.modules.learning.interface.controller.learning_stats_controller import (
    learning_stats_router,
)
from app.modules.taxonomy.interface.controller.tag_controller import tag_router
from app.modules.taxonomy.interface.controller.category_controller import (
    category_router,
)
from app.modules.taxonomy.interface.controller.curriculum_tag_controller import (
    curriculum_tag_router,
)

from app.modules.social.interface.controller.like_controller import like_router
from app.modules.social.interface.controller.comment_controller import comment_router
from app.modules.social.interface.controller.bookmark_controller import bookmark_router
from app.modules.social.interface.controller.social_controller import social_router
from app.modules.feed.interface.controller.feed_controller import feed_router  # 추가
from app.modules.social.interface.controller.follow_controller import follow_router


v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(user_router)
v1_router.include_router(curriculum_router)
v1_router.include_router(week_router)
v1_router.include_router(lesson_router)
v1_router.include_router(summary_router)
v1_router.include_router(user_summary_router)
v1_router.include_router(feedback_router)
# v1_router.include_router(curriculum_feedback_router)
v1_router.include_router(user_feedback_router)
v1_router.include_router(learning_stats_router)
v1_router.include_router(tag_router)
v1_router.include_router(category_router)
v1_router.include_router(curriculum_tag_router)
v1_router.include_router(like_router)
v1_router.include_router(comment_router)
v1_router.include_router(bookmark_router)
v1_router.include_router(social_router)
v1_router.include_router(feed_router)
v1_router.include_router(follow_router)
