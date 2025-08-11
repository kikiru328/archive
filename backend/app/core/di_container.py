from dependency_injector import containers, providers

# from dependency_injector.wiring import Provide
from app.common.cache import redis_client
from app.common.db.session import get_session

# from app.common.llm.openai_client import OpenAILLMClient
from app.common.llm.langchain_client import LangChainLLMClient
from app.common.monitoring.metrics_collector import MetricsService
from app.modules.admin.application.service.admin_curriculum_service import (
    AdminCurriculumService,
)
from app.modules.admin.infrastructure.repository.admin_curriculum_repository import (
    AdminCurriculumRepository,
)
from app.modules.curriculum.application.service.curriculum_service import (
    CurriculumService,
)

from app.modules.curriculum.domain.service.curriculum_domain_service import (
    CurriculumDomainService,
)
from app.modules.curriculum.infrastructure.repository.curriculum_repo import (
    CurriculumRepository,
)

from app.modules.feed.core.di_container import FeedContainer
from app.modules.learning.application.service.learning_stats_service import (
    LearningStatsService,
)
from app.modules.learning.core.di_container import LearningContainer

from app.modules.social.application.service.follow_service import FollowService
from app.modules.social.core.di_container import SocialContainer
from app.modules.social.domain.service.follow_domain_service import FollowDomainService
from app.modules.social.infrastructure.repository.follow_repo import FollowRepository
from app.modules.taxonomy.application.service.category_service import CategoryService
from app.modules.taxonomy.application.service.curriculum_tag_service import (
    CurriculumTagService,
)
from app.modules.taxonomy.application.service.tag_service import TagService
from app.modules.taxonomy.domain.service.tag_domain_service import TagDomainService
from app.modules.taxonomy.infrastructure.repository.category_repo import (
    CategoryRepository,
)
from app.modules.taxonomy.infrastructure.repository.curriculum_tag import (
    CurriculumCategoryRepository,
    CurriculumTagRepository,
)
from app.modules.taxonomy.infrastructure.repository.tag_repo import TagRepository
from app.modules.user.domain.service.user_domain_service import UserDomainService
from app.core.config import get_settings
from app.modules.user.application.service.auth_service import AuthService
from app.modules.user.application.service.user_service import UserService
from app.modules.user.infrastructure.repository.user_repo import UserRepository
from ulid import ULID  # type: ignore

from app.utils.crypto import Crypto


class Container(containers.DeclarativeContainer):
    # setting
    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.modules.admin.interface.controller",
            "app.modules.user.interface.controller",
            "app.modules.curriculum.interface.controller",
            "app.modules.learning.interface.controller",
            "app.modules.taxonomy.interface.controller",
            "app.modules.social.interface.controller",
            "app.modules.feed.interface.controller.feed_controller",
        ]
    )

    config = providers.Singleton(get_settings)

    # db_session = providers.Factory(AsyncSessionLocal)
    db_session = providers.Resource(
        get_session,
    )

    # User
    user_repository = providers.Factory(
        UserRepository,
        session=db_session,
    )

    user_domain_service = providers.Factory(
        UserDomainService,
        user_repo=user_repository,
    )

    user_service = providers.Factory(
        UserService,
        user_repo=user_repository,
        user_domain_service=user_domain_service,
        ulid=providers.Singleton(ULID),
        crypto=providers.Singleton(Crypto),
    )

    # Auth
    auth_service = providers.Factory(
        AuthService,
        user_repo=user_repository,
        user_domain_service=user_domain_service,
        ulid=providers.Singleton(ULID),
        crypto=providers.Singleton(Crypto),
    )

    # LLM
    llm_client = providers.Singleton(
        # OpenAILLMClient,
        LangChainLLMClient,
        api_key=config.provided.llm_api_key,
        model="gpt-4o-mini",
    )

    # Social
    follow_repository = providers.Factory(
        FollowRepository,
        session=db_session,
    )

    follow_domain_service = providers.Factory(
        FollowDomainService,
        follow_repo=follow_repository,
        user_repo=user_repository,
    )

    follow_service = providers.Factory(
        FollowService,
        follow_repo=follow_repository,
        user_repo=user_repository,
        follow_domain_service=follow_domain_service,
        ulid=providers.Singleton(ULID),
    )

    # Curriculum
    curriculum_repository = providers.Factory(
        CurriculumRepository,
        session=db_session,
    )

    curriculum_domain_service = providers.Factory(
        CurriculumDomainService,
        curriculum_repo=curriculum_repository,
    )
    curriculum_service = providers.Factory(
        CurriculumService,
        curriculum_repo=curriculum_repository,
        curriculum_domain_service=curriculum_domain_service,
        llm_client=llm_client,
        follow_repo=follow_repository,
        ulid=providers.Singleton(ULID),
    )
    # Learning

    learning_container = providers.Container(
        LearningContainer,
        session=db_session,
        curriculum_repository=curriculum_repository,
        llm_client=llm_client,
    )
    summary_service = learning_container.summary_service
    summary_repository = learning_container.summary_repository
    feedback_service = learning_container.feedback_service
    feedback_repository = learning_container.feedback_repository

    learning_stats_service = providers.Factory(
        LearningStatsService,
        summary_repo=summary_repository,
        feedback_repo=feedback_repository,
        curriculum_repo=curriculum_repository,
    )

    # Taxonomy

    tag_repository = providers.Factory(
        TagRepository,
        session=db_session,
    )

    category_repository = providers.Factory(
        CategoryRepository,
        session=db_session,
    )

    curriculum_tag_repository = providers.Factory(
        CurriculumTagRepository,
        session=db_session,
    )

    curriculum_category_repository = providers.Factory(
        CurriculumCategoryRepository,
        session=db_session,
    )

    tag_domain_service = providers.Factory(
        TagDomainService,
        tag_repo=tag_repository,
        category_repo=category_repository,
        curriculum_tag_repo=curriculum_tag_repository,
        curriculum_category_repo=curriculum_category_repository,
    )

    tag_service = providers.Factory(
        TagService,
        tag_repo=tag_repository,
        tag_domain_service=tag_domain_service,
        ulid=providers.Singleton(ULID),
    )

    category_service = providers.Factory(
        CategoryService,
        category_repo=category_repository,
        curriculum_category_repo=curriculum_category_repository,
        tag_domain_service=tag_domain_service,
        ulid=providers.Singleton(ULID),
    )

    curriculum_tag_service = providers.Factory(
        CurriculumTagService,
        tag_domain_service=tag_domain_service,
        curriculum_tag_repo=curriculum_tag_repository,
        curriculum_category_repo=curriculum_category_repository,
        curriculum_repo=curriculum_repository,
        ulid=providers.Singleton(ULID),
    )

    social_container = providers.Container(
        SocialContainer,
        session=db_session,
        curriculum_repository=curriculum_repository,
        user_repository=user_repository,
    )
    like_service = social_container.like_service
    comment_service = social_container.comment_service
    bookmark_service = social_container.bookmark_service

    follow_domain_service = providers.Factory(
        FollowDomainService,
        follow_repo=follow_repository,
        user_repo=user_repository,
    )

    follow_service = providers.Factory(
        FollowService,
        follow_repo=follow_repository,
        user_repo=user_repository,
        follow_domain_service=follow_domain_service,
        ulid=providers.Singleton(ULID),
    )

    feed_container = providers.Container(
        FeedContainer,
        session=db_session,
    )

    feed_service = feed_container.feed_service
    feed_repository = feed_container.feed_repository

    admin_curriculum_repository = providers.Factory(
        AdminCurriculumRepository, session=db_session
    )
    admin_curriculum_service = providers.Factory(
        AdminCurriculumService, repo=admin_curriculum_repository
    )

    metrics_service = providers.Factory(
        MetricsService,
        session=db_session,
        redis_client=providers.Singleton(lambda: redis_client),
        update_interval=30,
    )
