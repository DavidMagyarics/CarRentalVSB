"""FastAPI application (deployment diagram: backend container, uvicorn on :8000)."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import models  # noqa: F401 - register the ORM classes on Base.metadata
from .config import Settings
from .database import Base, make_engine, make_session_factory
from .errors import DomainError
from .routers import auth, cars, reservations
from .seed import seed_demo_data
from .services.notification import NotificationService, create_notification_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app(
    settings: Settings | None = None, notifier: NotificationService | None = None
) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = make_engine(settings.database_url)
    session_factory = make_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(engine)
        if settings.seed_demo_data:
            with session_factory() as db:
                seed_demo_data(db)
        yield
        engine.dispose()

    app = FastAPI(title="CarRentalVSB API", version="1.0.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    # Chosen once, at startup: e-mail when SMTP_HOST is set, otherwise logging.
    app.state.notifier = notifier or create_notification_service(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def _domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=headers)

    @app.get("/", tags=["health"])
    def root() -> dict:
        return {"name": "CarRentalVSB API", "status": "ok", "docs": "/docs"}

    app.include_router(auth.router)
    app.include_router(cars.router)
    app.include_router(reservations.router)
    return app


app = create_app()
