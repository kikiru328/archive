from typing import Any


class Password:
    __slots__ = ("_hashed",)

    def __init__(self, hashed: str) -> None:
        if not isinstance(hashed, str) or not hashed.strip():  # type: ignore
            raise ValueError("Hashed password must be a non-empty string")

        self._hashed: str = hashed

    @property
    def value(self) -> str:
        """return hashed password"""
        return self._hashed

    def __str__(self) -> str:
        return "****"

    def __repr__(self) -> str:
        return "<Password ****>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Password) and self._hashed == other._hashed

    def __hash__(self) -> int:
        return hash(self._hashed)
