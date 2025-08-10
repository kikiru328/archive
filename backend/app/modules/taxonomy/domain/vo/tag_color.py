import re


class TagColor:
    """
    태그 색상을 표현하는 VO.
    헥스 색상 코드 형식 (#FFFFFF)
    """

    __slots__ = ("_value",)

    _HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise ValueError(f"TagColor must be a string, got {type(raw).__name__}")

        cleaned = raw.strip().upper()
        if not cleaned:
            raise ValueError("색상은 공백일 수 없습니다")

        if not self._HEX_COLOR_PATTERN.match(cleaned):
            raise ValueError("색상은 #FFFFFF 형식의 헥스 코드여야 합니다")

        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TagColor) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<TagColor {self._value}>"

    def __str__(self) -> str:
        return self._value
