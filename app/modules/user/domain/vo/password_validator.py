import re


class PasswordValidator:
    MIN_LENGTH = 8
    MAX_LENGTH = 64

    _PASSWORD_RE: re.Pattern[str] = re.compile(
        r"""
        ^(?=.*[A-Z])          # 대문자
         (?=.*[a-z])          # 소문자
         (?=.*\d)             # 숫자
         (?=.*[^A-Za-z0-9])   # 특수문자 (공백 제외)
         [^\s]{8,64}$         # 전체 길이 및 공백 금지
        """,
        re.VERBOSE,
    )

    @staticmethod
    def validate(raw: str) -> None:
        """validate password"""
        if not isinstance(raw, str) or not raw.strip():  # type: ignore
            raise ValueError("Password must be a string")

        if not PasswordValidator._PASSWORD_RE.match(raw):
            raise ValueError(
                f"비밀번호는 {PasswordValidator.MIN_LENGTH}-{PasswordValidator.MAX_LENGTH}자로 "
                + "대소문자, 숫자, 특수문자를 포함해야 합니다"
            )

    @staticmethod
    def is_valid(raw: str) -> bool:
        """return password validate result"""
        try:
            PasswordValidator.validate(raw)
            return True
        except ValueError:
            return False
