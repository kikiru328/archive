class CurriculumNotFoundError(Exception):
    """커리큘럼을 찾을 수 없음"""

    pass


class CurriculumCountOverError(Exception):
    """커리큘럼 개수 초과"""

    pass


class WeekScheduleNotFoundError(Exception):
    """주차 스케줄을 찾을 수 없음"""

    pass


class WeekIndexOutOfRangeError(Exception):
    """주차 인덱스 범위 초과"""

    pass


class InvalidCurriculumStructureError(Exception):
    """잘못된 커리큘럼 구조"""

    pass


class CurriculumAccessDeniedError(Exception):
    """커리큘럼 접근 권한 없음"""

    pass


class LLMGenerationError(Exception):
    """LLM 생성 실패"""

    pass


class InvalidLLMResponseError(Exception):
    """잘못된 LLM 응답"""

    pass
