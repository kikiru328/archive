import re
from typing import List


class TagName:
    """
    태그 이름을 표현하는 VO.
    1자 이상 20자 이하, 영문/한글/숫자만 허용 (공백 불허)
    """

    __slots__ = ("_value",)

    MIN_LENGTH = 1
    MAX_LENGTH = 20

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise ValueError(f"TagName must be a string, got {type(raw).__name__}")

        cleaned = raw.strip().lower()  # 소문자로 정규화
        if not cleaned:
            raise ValueError("태그 이름은 공백일 수 없습니다")

        length = len(cleaned)
        if length < self.MIN_LENGTH:
            raise ValueError(f"태그 이름은 최소 {self.MIN_LENGTH}자 이상이어야 합니다")
        if length > self.MAX_LENGTH:
            raise ValueError(f"태그 이름은 최대 {self.MAX_LENGTH}자 이하이어야 합니다")

        # 허용되는 문자 검사 (영문, 한글, 숫자만, 공백 불허)
        if not re.match(r"^[a-zA-Z0-9가-힣]+$", cleaned):
            raise ValueError(
                "태그 이름은 영문, 한글, 숫자만 사용할 수 있습니다 (공백 불허)"
            )

        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TagName) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<TagName {self._value!r}>"

    def __str__(self) -> str:
        return self._value

    @classmethod
    def from_list(cls, tag_names: List[str]) -> List["TagName"]:
        """문자열 리스트에서 TagName 리스트 생성"""
        return [cls(name) for name in tag_names if name.strip()]
