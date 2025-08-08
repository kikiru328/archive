class FeedbackScore:
    """피드백 점수를 표현하는 VO"""

    __slots__ = ("_value",)

    MIN_SCORE = 0.0
    MAX_SCORE = 10.0

    def __init__(self, raw: int | float) -> None:
        if not isinstance(raw, (int, float)):
            raise TypeError(
                f"FeedbackScore must be int or float, got {type(raw).__name__}"
            )

        value = float(raw)
        if not (self.MIN_SCORE <= value <= self.MAX_SCORE):
            raise ValueError(
                f"FeedbackScore must be between {self.MIN_SCORE} and {self.MAX_SCORE}, got {value}"
            )

        self._value = value

    @property
    def value(self) -> float:
        return self._value

    def __str__(self) -> str:
        return f"{self._value}/10"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FeedbackScore) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<FeedbackScore {self._value}>"
