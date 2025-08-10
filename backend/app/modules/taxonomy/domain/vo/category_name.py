import re


class CategoryName:
    """
    카테고리 이름을 표현하는 VO.
    2자 이상 30자 이하, 영문/한글/숫자/공백/하이픈만 허용
    """

    __slots__ = ("_value",)

    MIN_LENGTH = 2
    MAX_LENGTH = 30

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise ValueError(f"CategoryName must be a string, got {type(raw).__name__}")

        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("카테고리 이름은 공백일 수 없습니다")

        length = len(cleaned)
        if length < self.MIN_LENGTH:
            raise ValueError(
                f"카테고리 이름은 최소 {self.MIN_LENGTH}자 이상이어야 합니다"
            )
        if length > self.MAX_LENGTH:
            raise ValueError(
                f"카테고리 이름은 최대 {self.MAX_LENGTH}자 이하이어야 합니다"
            )

        # 허용되는 문자 검사 (영문, 한글, 숫자, 공백, 하이픈)
        if not re.match(r"^[a-zA-Z0-9가-힣\s\-]+$", cleaned):
            raise ValueError(
                "카테고리 이름은 영문, 한글, 숫자, 공백, 하이픈만 사용할 수 있습니다"
            )

        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CategoryName) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<CategoryName {self._value!r}>"

    def __str__(self) -> str:
        return self._value
