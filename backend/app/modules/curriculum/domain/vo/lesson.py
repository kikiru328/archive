class Lesson:
    """Lesson Unit"""

    __slots__ = ("_value",)

    MIN_LENGTH = 1
    MAX_LENGTH = 100

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):  # type: ignore
            raise ValueError(f"Lesson must be a string, got {type(raw).__name__}")

        cleaned = raw.strip()

        if not cleaned:
            raise ValueError("Lesson cannot be empty")

        length = len(cleaned)
        if length < self.MIN_LENGTH:
            raise ValueError(f"Lesson must be at least {self.MIN_LENGTH} character")
        if length > self.MAX_LENGTH:
            raise ValueError(f"Lesson cannot exceed {self.MAX_LENGTH} characters")

        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"<Lesson {self._value!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Lesson) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
