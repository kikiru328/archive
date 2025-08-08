class FeedbackComment:
    """피드백 코멘트를 표현하는 VO"""

    __slots__ = ("_value",)

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise TypeError(
                f"FeedbackComment must be a string, got {type(raw).__name__}"
            )

        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("FeedbackComment cannot be empty or whitespace only")

        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FeedbackComment) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        length = len(self._value)
        return f"<FeedbackComment length={length}>"

    def __str__(self) -> str:
        return self._value
