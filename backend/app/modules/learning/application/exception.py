class SummaryNotFoundError(Exception):
    """요약을 찾을 수 없음"""

    pass


class FeedbackNotFoundError(Exception):
    """피드백을 찾을 수 없음"""

    pass


class FeedbackAlreadyExistsError(Exception):
    """피드백이 이미 존재함"""

    pass


class SummaryAccessDeniedError(Exception):
    """요약 접근 권한 없음"""

    pass


class FeedbackAccessDeniedError(Exception):
    """피드백 접근 권한 없음"""

    pass


class InvalidSummaryContentError(Exception):
    """잘못된 요약 내용"""

    pass


class InvalidFeedbackScoreError(Exception):
    """잘못된 피드백 점수"""

    pass


class LLMFeedbackGenerationError(Exception):
    """LLM 피드백 생성 실패"""

    pass
