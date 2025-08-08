import re
from typing import Any


class Email:
    __slots__ = ("_value",)

    _EMAIL_RE: re.Pattern[str] = re.compile(
        r"^(?!.*\.\.)"  # anywhere: no consecutive dots
        + r"[A-Za-z0-9._%+-]+"
        + r"@"
        + r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("Email must be a string")

        cleaned = raw.lower().strip()

        if not cleaned:
            raise ValueError("Email cannot be empty")

        if not self._EMAIL_RE.match(cleaned):
            raise ValueError("Invalid email format")

        self._value: str = cleaned

    @property
    def value(self) -> str:
        """return cleaned Email"""
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"<Email {self._value}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Email) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
