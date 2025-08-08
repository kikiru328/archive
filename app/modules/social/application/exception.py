# app/modules/social/application/exception.py


class LikeNotFoundError(Exception):
    """좋아요를 찾을 수 없음"""

    pass


class CommentNotFoundError(Exception):
    """댓글을 찾을 수 없음"""

    pass


class BookmarkNotFoundError(Exception):
    """북마크를 찾을 수 없음"""

    pass


class LikeAlreadyExistsError(Exception):
    """좋아요가 이미 존재함"""

    pass


class BookmarkAlreadyExistsError(Exception):
    """북마크가 이미 존재함"""

    pass


class SocialAccessDeniedError(Exception):
    """소셜 기능 접근 권한 없음"""

    pass


class CommentAccessDeniedError(Exception):
    """댓글 접근 권한 없음"""

    pass


class InvalidCommentContentError(Exception):
    """잘못된 댓글 내용"""

    pass


class CurriculumNotAccessibleError(Exception):
    """커리큘럼에 접근할 수 없음"""

    pass


class FollowNotFoundError(Exception):
    """팔로우 관계를 찾을 수 없음"""

    pass


class AlreadyFollowingError(Exception):
    """이미 팔로우 중임"""

    pass


class NotFollowingError(Exception):
    """팔로우하지 않고 있음"""

    pass


class SelfFollowError(Exception):
    """자기 자신을 팔로우할 수 없음"""

    pass


class UserNotFoundError(Exception):
    """사용자를 찾을 수 없음"""

    pass


class FollowAccessDeniedError(Exception):
    """팔로우 접근 권한 없음"""

    pass


class FeedNotFoundError(Exception):
    """피드를 찾을 수 없음"""

    pass


class FeedCacheError(Exception):
    """피드 캐시 오류"""

    pass
