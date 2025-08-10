class SummaryContent:
    """요약 내용을 표현하는 VO"""

    __slots__ = ("_value",)

    MIN_LENGTH = 100
    MAX_LENGTH = 5000

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise ValueError(
                f"SummaryContent must be a string, got {type(raw).__name__}"
            )

        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("SummaryContent cannot be empty")

        length = len(cleaned)
        if length < self.MIN_LENGTH:
            raise ValueError(
                f"요약 내용은 {self.MIN_LENGTH}자 이상이어야 합니다 (현재 {length}자)"
            )
        if length > self.MAX_LENGTH:
            raise ValueError(
                f"요약 내용은 {self.MAX_LENGTH}자 이하이어야 합니다 (현재 {length}자)"
            )

        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def length(self) -> int:
        return len(self._value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SummaryContent) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<SummaryContent length={len(self._value)}>"

    def __str__(self) -> str:
        return self._value
