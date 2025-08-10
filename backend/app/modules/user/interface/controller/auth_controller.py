from typing import Annotated
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from app.core.di_container import Container
from app.modules.user.application.dto.user_dto import CreateUserCommand, UserDTO
from app.modules.user.application.service.auth_service import AuthService
from app.modules.user.interface.schema.auth_schema import (
    SignUpBody,
    SignUpResponse,
    TokenResponse,
)


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/signup", response_model=SignUpResponse)
@inject
async def signup(
    body: SignUpBody,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> SignUpResponse:
    command = CreateUserCommand(
        email=body.email,
        name=body.name,
        password=body.password,
    )
    user_dto: UserDTO = await auth_service.signup(command)
    return SignUpResponse.from_dto(user_dto)


@auth_router.post("/login", response_model=TokenResponse)
@inject
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> TokenResponse:
    access_token, role = await auth_service.login(
        email=form_data.username,  # 직접 전달
        password=form_data.password,
    )
    return TokenResponse(access_token=access_token, role=role)
