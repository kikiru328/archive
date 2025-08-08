import re
from typing import Any


class Name:
    __slots__ = ("_value",)

    MIN_LENGTH = 2
    MAX_LENGTH = 32

    _NAME_RE: re.Pattern[str] = re.compile(r"^[A-Za-z0-9\uAC00-\uD7A3 ]+$")

    def __init__(self, raw: str) -> None:

        if not isinstance(raw, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("Name must be a string")

        cleaned: str = raw.strip()

        if not cleaned:
            raise ValueError("Name cannot be empty")

        if not (self.MIN_LENGTH <= len(cleaned) <= self.MAX_LENGTH):
            raise ValueError(
                f"Name length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH} characters"
            )

        if not self._NAME_RE.match(cleaned):
            raise ValueError(
                "Name can only contain Korean, English letters and numbers"
            )

        self._value: str = cleaned

    @property
    def value(self) -> str:
        """return cleaned value"""
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"<Name {self._value}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Name) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
