from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.modules.user.application.dto.user_dto import UserDTO


class SignUpBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=64)


class SignUpResponse(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    created_at: datetime

    @classmethod
    def from_dto(cls, user_dto: UserDTO) -> "SignUpResponse":
        return cls(
            name=user_dto.name,
            email=user_dto.email,
            created_at=user_dto.created_at,
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
