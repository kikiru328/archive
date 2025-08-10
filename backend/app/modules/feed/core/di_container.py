from dependency_injector import containers, providers

from app.modules.feed.application.service.feed_service import FeedService
from app.modules.feed.infrastructure.repository.feed_repo import FeedRepository


class FeedContainer(containers.DeclarativeContainer):
    session: providers.Dependency[object] = providers.Dependency()

    feed_repository = providers.Factory(
        FeedRepository,
        session=session,
    )

    feed_service = providers.Factory(
        FeedService,
        feed_repo=feed_repository,
    )
