from dependency_injector import containers, providers
from ulid import ULID  # type: ignore

from app.modules.social.application.service.like_service import LikeService
from app.modules.social.application.service.comment_service import CommentService
from app.modules.social.application.service.bookmark_service import BookmarkService
from app.modules.social.domain.service.social_domain_service import SocialDomainService
from app.modules.social.infrastructure.repository.like_repo import LikeRepository
from app.modules.social.infrastructure.repository.comment_repo import CommentRepository
from app.modules.social.infrastructure.repository.bookmark_repo import (
    BookmarkRepository,
)


class SocialContainer(containers.DeclarativeContainer):
    # Dependencies
    session: providers.Dependency[object] = providers.Dependency()
    curriculum_repository: providers.Dependency[object] = providers.Dependency()

    # Repositories
    like_repository = providers.Factory(
        LikeRepository,
        session=session,
    )

    comment_repository = providers.Factory(
        CommentRepository,
        session=session,
    )

    bookmark_repository = providers.Factory(
        BookmarkRepository,
        session=session,
    )

    # Domain Service
    social_domain_service = providers.Factory(
        SocialDomainService,
        like_repo=like_repository,
        comment_repo=comment_repository,
        bookmark_repo=bookmark_repository,
        curriculum_repo=curriculum_repository,
    )

    # Application Services
    like_service = providers.Factory(
        LikeService,
        like_repo=like_repository,
        social_domain_service=social_domain_service,
        ulid=providers.Singleton(ULID),
    )

    comment_service = providers.Factory(
        CommentService,
        comment_repo=comment_repository,
        social_domain_service=social_domain_service,
        ulid=providers.Singleton(ULID),
    )

    bookmark_service = providers.Factory(
        BookmarkService,
        bookmark_repo=bookmark_repository,
        social_domain_service=social_domain_service,
        ulid=providers.Singleton(ULID),
    )
