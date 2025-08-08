# app/modules/user/interface/controller/auth_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from dependency_injector.wiring import inject, Provide

from app.modules.user.application.service.auth_service import AuthService
from app.modules.user.application.dto.user_dto import CreateUserCommand, UserDTO
from app.modules.user.application.exception import (
    ExistEmailError,
    ExistNameError,
    EmailNotFoundError,
    PasswordIncorrectError,
)
from app.core.di_container import Container


router = APIRouter()

pattern = r"^[A-Za-z0-9\uAC00-\uD7A3 ]+$"


class SignUpRequest(BaseModel):
    # ─ default 값(…)을 첫 번째 인자로,
    #   그 뒤에 제약조건을 키워드 인자로 명시해야 합니다.
    name: str = Field(..., min_length=2, max_length=32, pattern=pattern)  # type: ignore
    email: EmailStr
    password: str = Field(..., min_length=8)


# 2. 회원가입 엔드포인트
@router.post("/auth/signup", response_model=UserDTO)
@inject
async def signup(
    req: SignUpRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    try:
        cmd = CreateUserCommand(
            name=req.name,
            email=req.email,
            password=req.password,
        )
        return await auth_service.signup(cmd)
    except (ExistEmailError, ExistNameError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 3. 로그인 엔드포인트
@router.post("/auth/login")
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    try:
        access_token, role = await auth_service.login(
            email=form_data.username, password=form_data.password
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": role,
        }
    except (EmailNotFoundError, PasswordIncorrectError):
        # 이메일 미발견 혹은 비밀번호 불일치 시 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
