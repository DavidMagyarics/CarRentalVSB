"""FastAPI dependencies: DB session, settings, services, current user, clock."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Annotated, Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import Settings
from .models import User
from .services.auth_service import AuthService
from .services.fleet_service import FleetService
from .services.notification import NotificationService
from .services.reservation_service import ReservationService

bearer_scheme = HTTPBearer(auto_error=False)


def get_db(request: Request) -> Iterator[Session]:
    db = request.app.state.session_factory()
    try:
        yield db
    finally:
        db.close()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_notifier(request: Request) -> NotificationService:
    return request.app.state.notifier


def get_clock() -> Callable[[], datetime]:
    """Overridable in tests to simulate "now"."""
    return datetime.now


DbDep = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_auth_service(db: DbDep, settings: SettingsDep) -> AuthService:
    return AuthService(db, settings)


def get_fleet_service(db: DbDep) -> FleetService:
    return FleetService(db)


def get_reservation_service(
    db: DbDep,
    notifier: Annotated[NotificationService, Depends(get_notifier)],
    clock: Annotated[Callable[[], datetime], Depends(get_clock)],
) -> ReservationService:
    return ReservationService(db, notifier, clock)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
FleetServiceDep = Annotated[FleetService, Depends(get_fleet_service)]
ReservationServiceDep = Annotated[ReservationService, Depends(get_reservation_service)]


def get_current_user(
    auth: AuthServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """401 when there is no token, or it is invalid / expired."""
    token = credentials.credentials if credentials else None
    return auth.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]
