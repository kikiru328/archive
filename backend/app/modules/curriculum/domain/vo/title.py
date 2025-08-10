class Title:
    __slots__ = ("_value",)

    MIN_LENGTH = 2
    MAX_LENGTH = 50

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):  # type: ignore
            raise ValueError("Titie must be string")

        cleaned = raw.strip()

        if not cleaned:
            raise ValueError("Title cannot be empty")

        if not (self.MIN_LENGTH <= len(cleaned) <= self.MAX_LENGTH):
            raise ValueError(
                f"Title length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH} characters"
            )

        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"<Title {self._value!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Title) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
