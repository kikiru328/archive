class FeedNotFoundError(Exception):
    """피드를 찾을 수 없음"""

    pass


class FeedCacheError(Exception):
    """피드 캐시 오류"""

    pass
