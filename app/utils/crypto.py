import logging

# bcrypt 핸들러 로깅을 WARNING 이상만 표시하도록

from passlib.context import CryptContext

logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.WARNING)


class Crypto:
    def __init__(self) -> None:
        self.password_context: CryptContext = CryptContext(
            schemes=["bcrypt"], deprecated="auto"
        )

    def encrypt(self, secret: str) -> str:
        return self.password_context.hash(secret)

    def verify(self, secret: str, hash: str) -> bool:
        return self.password_context.verify(secret, hash)
