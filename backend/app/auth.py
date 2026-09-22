"""Password hashing and JWT access tokens for the authentication boundary.

Dev-only secret: for the seminar project the signing key defaults to a
fixed string so the app runs out of the box. Set the SECRET_KEY environment
variable to override it (required for any real deployment).
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

SECRET_KEY = os.environ.get("SECRET_KEY", "carrentalvsb-dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    try:
        return int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        return None
