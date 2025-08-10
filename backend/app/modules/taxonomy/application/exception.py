class TagNotFoundError(Exception):
    """태그를 찾을 수 없음"""

    pass


class CategoryNotFoundError(Exception):
    """카테고리를 찾을 수 없음"""

    pass


class DuplicateTagError(Exception):
    """중복 태그 오류"""

    pass


class DuplicateCategoryError(Exception):
    """중복 카테고리 오류"""

    pass


class TagAccessDeniedError(Exception):
    """태그 접근 권한 없음"""

    pass


class CategoryAccessDeniedError(Exception):
    """카테고리 접근 권한 없음"""

    pass


class InvalidTagNameError(Exception):
    """잘못된 태그 이름"""

    pass


class InvalidCategoryNameError(Exception):
    """잘못된 카테고리 이름"""

    pass


class InvalidColorFormatError(Exception):
    """잘못된 색상 형식"""

    pass


class CategoryInUseError(Exception):
    """사용 중인 카테고리 삭제 불가"""

    pass


class TagInUseError(Exception):
    """사용 중인 태그 삭제 불가"""

    pass


class TagLimitExceededError(Exception):
    """태그 개수 제한 초과"""

    pass


class InactiveCategoryAssignmentError(Exception):
    """비활성화된 카테고리 할당 불가"""

    pass
