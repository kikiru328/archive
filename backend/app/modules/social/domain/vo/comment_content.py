from typing import Literal


class CommentContent:
    """댓글 내용을 표현하는 VO"""

    __slots__: tuple[Literal["_value"]] = ("_value",)

    MIN_LENGTH = 1
    MAX_LENGTH = 1000

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise ValueError(
                f"CommentContent must be a string, got {type(raw).__name__}"
            )

        cleaned: str = raw.strip()
        if not cleaned:
            raise ValueError("댓글 내용은 공백일 수 없습니다")

        length: int = len(cleaned)
        if length < self.MIN_LENGTH:
            raise ValueError(f"댓글 내용은 최소 {self.MIN_LENGTH}자 이상이어야 합니다")
        if length > self.MAX_LENGTH:
            raise ValueError(f"댓글 내용은 최대 {self.MAX_LENGTH}자 이하이어야 합니다")

        self._value: str = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def length(self) -> int:
        return len(self._value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CommentContent) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<CommentContent length={len(self._value)}>"

    def __str__(self) -> str:
        return self._value
