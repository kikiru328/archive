from dependency_injector import containers, providers
from ulid import ULID  # type: ignore

from app.modules.learning.application.service.feedback_service import FeedbackService
from app.modules.learning.application.service.learning_stats_service import (
    LearningStatsService,
)
from app.modules.learning.application.service.summary_service import SummaryService
from app.modules.learning.domain.service.learning_domain_service import (
    LearningDomainService,
)
from app.modules.learning.infrastructure.repository.feedback_repo import (
    FeedbackRepository,
)
from app.modules.learning.infrastructure.repository.summary_repo import (
    SummaryRepository,
)


class LearningContainer(containers.DeclarativeContainer):
    session: providers.Dependency[object] = providers.Dependency()
    curriculum_repository: providers.Dependency[object] = providers.Dependency()
    llm_client: providers.Dependency[object] = providers.Dependency()

    summary_repository = providers.Factory(
        SummaryRepository,
        session=session,
    )

    feedback_repository = providers.Factory(
        FeedbackRepository,
        session=session,
    )

    learning_domain_service = providers.Factory(
        LearningDomainService,
        summary_repo=summary_repository,
        feedback_repo=feedback_repository,
        curriculum_repo=curriculum_repository,
    )

    summary_service = providers.Factory(
        SummaryService,
        summary_repo=summary_repository,
        learning_domain_service=learning_domain_service,
        ulid=providers.Singleton(ULID),
    )

    feedback_service = providers.Factory(
        FeedbackService,
        feedback_repo=feedback_repository,
        summary_repo=summary_repository,
        curriculum_repo=curriculum_repository,
        learning_domain_service=learning_domain_service,
        llm_client=llm_client,
        ulid=providers.Singleton(ULID),
    )

    learning_stats_service = providers.Factory(
        LearningStatsService,
        summary_repo=summary_repository,
        feedback_repo=feedback_repository,
        curriculum_repo=curriculum_repository,
    )
