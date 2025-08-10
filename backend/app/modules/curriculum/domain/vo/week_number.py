class WeekNumber:

    __slots__ = ("_value",)

    MIN_WEEK = 1
    MAX_WEEK = 24

    def __init__(self, raw: int) -> None:
        if not isinstance(raw, int):  # type: ignore
            raise ValueError(f"WeekNumber must be an integer, got {type(raw).__name__}")

        if not (self.MIN_WEEK <= raw <= self.MAX_WEEK):
            raise ValueError(
                f"WeekNumber must be between {self.MIN_WEEK} and {self.MAX_WEEK}, got {raw}"
            )

        self._value = raw

    @property
    def value(self) -> int:
        return self._value

    def next(self) -> "WeekNumber":
        """return next week number"""
        if self._value >= self.MAX_WEEK:
            raise ValueError("Cannot get next week beyond maximum")
        return WeekNumber(self._value + 1)

    def previous(self) -> "WeekNumber":
        """return previous week number"""
        if self._value <= self.MIN_WEEK:
            raise ValueError("Cannot get previous week below minimum")
        return WeekNumber(self._value - 1)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, WeekNumber) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<WeekNumber {self._value}>"

    def __lt__(self, other: "WeekNumber") -> bool:
        return self._value < other._value

    def __le__(self, other: "WeekNumber") -> bool:
        return self._value <= other._value

    def __gt__(self, other: "WeekNumber") -> bool:
        return self._value > other._value

    def __ge__(self, other: "WeekNumber") -> bool:
        return self._value >= other._value
