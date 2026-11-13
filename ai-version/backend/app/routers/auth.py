from __future__ import annotations

from fastapi import APIRouter, status

from ..deps import AuthServiceDep, CurrentUser
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, auth: AuthServiceDep) -> TokenOut:
    """UC1 - 201 {token, user}; 409 e-mail already registered; 422 invalid input."""
    token, user = auth.create_user(body.name, body.email, body.password)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, auth: AuthServiceDep) -> TokenOut:
    """UC2 - 200 {token, user}; 401 invalid credentials."""
    token, user = auth.authenticate_user(body.email, body.password)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
