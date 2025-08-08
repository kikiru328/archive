from enum import StrEnum


class Visibility(StrEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"

    def is_public(self) -> bool:
        return self == Visibility.PUBLIC

    def is_private(self) -> bool:
        return self == Visibility.PRIVATE
