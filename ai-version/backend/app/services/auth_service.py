"""AuthService - UC1 Register, UC2 Log in, current user from JWT (UC6)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import Settings
from ..errors import (
    MSG_EMAIL_TAKEN,
    MSG_INVALID_CREDENTIALS,
    MSG_INVALID_TOKEN,
    MSG_NOT_AUTHENTICATED,
    Conflict,
    Unauthorized,
)
from ..models import User, UserRole
from ..security import create_access_token, decode_access_token, hash_password


class AuthService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings

    # --- public -------------------------------------------------------------
    def create_user(self, name: str, email: str, password: str) -> tuple[str, User]:
        """UC1: 409 when the e-mail is taken, otherwise a CUSTOMER + JWT."""
        email = email.strip().lower()
        if self.get_user_by_email(email) is not None:
            raise Conflict(MSG_EMAIL_TAKEN)
        user = User(
            name=name,
            email=email,
            password_hash=self.hash_password(password),
            role=UserRole.CUSTOMER,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.create_access_token(user), user

    def authenticate_user(self, email: str, password: str) -> tuple[str, User]:
        """UC2: 401 with the same message for unknown e-mail and wrong password."""
        user = self.get_user_by_email(email.strip().lower())
        if user is None or not user.check_password(password):
            raise Unauthorized(MSG_INVALID_CREDENTIALS)
        return self.create_access_token(user), user

    def get_current_user(self, token: str | None) -> User:
        if not token:
            raise Unauthorized(MSG_NOT_AUTHENTICATED)
        user_id = decode_access_token(
            token, self.settings.secret_key, self.settings.jwt_algorithm
        )
        if user_id is None:
            raise Unauthorized(MSG_INVALID_TOKEN)
        user = self.db.get(User, user_id)
        if user is None:
            raise Unauthorized(MSG_INVALID_TOKEN)
        return user

    # --- private ------------------------------------------------------------
    def get_user_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    @staticmethod
    def hash_password(password: str) -> str:
        return hash_password(password)

    def create_access_token(self, user: User) -> str:
        return create_access_token(
            user.id,
            user.role,
            self.settings.secret_key,
            self.settings.jwt_algorithm,
            self.settings.access_token_expire_minutes,
        )
