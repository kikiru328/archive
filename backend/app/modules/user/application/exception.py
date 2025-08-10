class UserNotFoundError(Exception): ...


class ExistNameError(Exception): ...


class ExistEmailError(Exception): ...


class EmailNotFoundError(Exception): ...  # HTTP_401_UNAUTHORIZED


class PasswordIncorrectError(Exception): ...  # HTTP_401_UNAUTHORIZED
