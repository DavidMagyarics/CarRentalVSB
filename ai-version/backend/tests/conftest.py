from __future__ import annotations

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.deps import get_clock
from app.main import create_app
from app.models import Branch, Car, User, UserRole
from app.security import hash_password
from app.services.notification import NotificationService

# Monday 7 January 2030, 07:00 - before opening, so a Monday 09:00 pickup is in the future.
NOW = datetime(2030, 1, 7, 7, 0)


class RecordingNotifier(NotificationService):
    def __init__(self) -> None:
        self.sent: list[tuple[int, str]] = []
        self.result = True

    def send_confirmation(self, reservation, user) -> bool:
        self.sent.append((reservation.id, user.email))
        return self.result


class Clock:
    def __init__(self, now: datetime):
        self.now = now

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def notifier() -> RecordingNotifier:
    return RecordingNotifier()


@pytest.fixture
def clock() -> Clock:
    return Clock(NOW)


@pytest.fixture
def app(notifier, clock):
    application = create_app(
        Settings(database_url="sqlite://", seed_demo_data=False, secret_key="test-secret-key-for-pytest-0123456789abcdef"),
        notifier=notifier,
    )
    application.dependency_overrides[get_clock] = lambda: clock
    return application


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db(app, client):
    session = app.state.session_factory()
    yield session
    session.close()


def _make_user(db, name, email, password, role) -> User:
    user = User(name=name, email=email, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    return user


def _login(client, email, password) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client, db):
    _make_user(db, "Admin", "admin@test.cz", "admin123", UserRole.ADMIN)
    return _login(client, "admin@test.cz", "admin123")


@pytest.fixture
def customer_headers(client, db):
    _make_user(db, "Customer", "customer@test.cz", "secret1", UserRole.CUSTOMER)
    return _login(client, "customer@test.cz", "secret1")


@pytest.fixture
def other_headers(client, db):
    _make_user(db, "Other", "other@test.cz", "secret2", UserRole.CUSTOMER)
    return _login(client, "other@test.cz", "secret2")


@pytest.fixture
def branches(db):
    items = [Branch(name="Ostrava", address="A 1"), Branch(name="Praha", address="B 2")]
    db.add_all(items)
    db.commit()
    return items


@pytest.fixture
def cars(db, branches):
    items = [
        Car(brand="Škoda", model="Fabia", year=2022, license_plate="1AB 0001", daily_price=800,
            hourly_price=100, category="Hatchback", transmission="Manual", fuel_type="Petrol",
            seats=5, branch=branches[0]),
        Car(brand="Tesla", model="Model 3", year=2024, license_plate="1AB 0002", daily_price=2000,
            hourly_price=250, category="Sedan", transmission="Automatic", fuel_type="Electric",
            seats=5, branch=branches[1]),
        Car(brand="Hyundai", model="Tucson", year=2023, license_plate="1AB 0003", daily_price=1500,
            hourly_price=170, category="SUV", transmission="Automatic", fuel_type="Hybrid",
            seats=5, branch=branches[0]),
    ]
    db.add_all(items)
    db.commit()
    return items


@pytest.fixture
def car(cars):
    return cars[0]


def reservation_body(car_id: int, start: str = "2030-01-07T09:00", end: str = "2030-01-09T10:00",
                     payment: str = "CASH") -> dict:
    return {"car_id": car_id, "start_date": start, "end_date": end, "payment_method": payment}
