from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import get_settings
from jose import JWTError, jwt

settings = get_settings()

SECRET_KEY: str = settings.secret_key
ALGORITHM: str = settings.algorithm


class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # 0729


@dataclass
class CurrentUser:
    id: str
    role: Role


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    payload = decode_access_token(token)
    sub = payload.get("sub")
    role_str = payload.get("role")
    if not sub or not role_str:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        role = Role(role_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid role")

    return CurrentUser(id=sub, role=role)


def create_access_token(
    *,
    subject: str,
    role: Role,
    expires_delta: timedelta | None = None,
) -> str:
    expire_dt: datetime = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=5)
    )
    to_encode: dict[str, Any] = {
        "sub": subject,
        "role": role.value,
        "exp": int(expire_dt.timestamp()),  # <-- int 형태
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
