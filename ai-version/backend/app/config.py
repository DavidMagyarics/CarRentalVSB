"""Application settings, read from environment variables (and backend/.env)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Load backend/.env if it exists (deployment diagram: SMTP_HOST in backend/.env).
load_dotenv(BACKEND_DIR / ".env")


def _bool(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _list(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass
class Settings:
    database_url: str = "sqlite:///./carrental.db"
    secret_key: str = "dev-secret-key-change-me-in-production-0123456789"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    cors_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    seed_demo_data: bool = True

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@carrental.local"
    smtp_use_tls: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()
        return cls(
            database_url=os.getenv("DATABASE_URL") or defaults.database_url,
            secret_key=os.getenv("SECRET_KEY") or defaults.secret_key,
            access_token_expire_minutes=int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
                or defaults.access_token_expire_minutes
            ),
            cors_origins=_list(os.getenv("CORS_ORIGINS"), defaults.cors_origins),
            seed_demo_data=_bool(os.getenv("SEED_DEMO_DATA"), True),
            smtp_host=os.getenv("SMTP_HOST", "").strip(),
            smtp_port=int(os.getenv("SMTP_PORT") or 587),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_from=os.getenv("SMTP_FROM") or defaults.smtp_from,
            smtp_use_tls=_bool(os.getenv("SMTP_USE_TLS"), True),
        )
