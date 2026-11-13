"""Unit tests: State pattern, price calculation, opening hours, notifications."""

from datetime import datetime

import pytest

from app.config import Settings
from app.errors import Conflict, Unprocessable
from app.models import Branch, Car, Reservation, User
from app.services.notification import (
    EmailNotificationService,
    LoggingNotificationService,
    create_notification_service,
)
from app.services.reservation_service import calculate_price, check_dates
from app.states import (
    BLOCKING_STATUSES,
    CancelledState,
    ConfirmedState,
    DraftState,
)

START = datetime(2030, 1, 7, 9, 0)
END = datetime(2030, 1, 9, 10, 0)


def _reservation(**kwargs) -> Reservation:
    return Reservation(start_date=START, end_date=END, total_price=0, payment_method="CASH", **kwargs)


# --- State pattern -------------------------------------------------------------
def test_new_reservation_starts_in_draft_state():
    r = _reservation()
    assert r.status == "DRAFT"
    assert isinstance(r.state, DraftState)
    assert r.blocks_car() is False


def test_pattern_scenario_from_the_diagram():
    r = _reservation()
    r.confirm()  # UC8: Draft -> Confirmed
    assert isinstance(r.state, ConfirmedState) and r.status == "CONFIRMED"
    assert r.blocks_car() is True
    r.cancel(now=datetime(2030, 1, 6, 12, 0))  # UC5: Confirmed (before pickup) -> Cancelled
    assert isinstance(r.state, CancelledState) and r.status == "CANCELLED"
    assert r.blocks_car() is False
    with pytest.raises(Conflict):  # Cancelled: rejected (409)
        r.confirm()


def test_draft_confirm_with_slot_taken_is_rejected():
    r = _reservation()
    with pytest.raises(Conflict) as exc:
        r.confirm(car_available=False)
    assert exc.value.status_code == 409
    assert r.status == "DRAFT"


def test_draft_cancel():
    r = _reservation()
    r.cancel()
    assert r.status == "CANCELLED"


def test_confirmed_confirm_again_is_rejected():
    r = _reservation(status="CONFIRMED")
    with pytest.raises(Conflict):
        r.confirm()


def test_confirmed_cancel_after_rental_started_is_rejected():
    r = _reservation(status="CONFIRMED")
    assert r.rental_started(now=START) is True
    with pytest.raises(Conflict):
        r.cancel(now=START)
    assert r.status == "CONFIRMED"


def test_cancelled_cancel_is_rejected():
    r = _reservation(status="CANCELLED")
    with pytest.raises(Conflict) as exc:
        r.cancel()
    assert exc.value.detail == "Rezervace je již zrušena"


def test_only_confirmed_blocks_the_car():
    assert BLOCKING_STATUSES == ("CONFIRMED",)


def test_overlaps_is_half_open():
    r = _reservation()
    assert r.overlaps(datetime(2030, 1, 8, 9, 0), datetime(2030, 1, 8, 10, 0))
    assert not r.overlaps(END, datetime(2030, 1, 10, 9, 0))
    assert not r.overlaps(datetime(2030, 1, 6, 9, 0), START)


# --- price calculation -------------------------------------------------------------
@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        (datetime(2030, 1, 7, 9), datetime(2030, 1, 8, 9), 800),        # exactly 1 day
        (datetime(2030, 1, 7, 9), datetime(2030, 1, 7, 12), 300),       # 3 h
        (datetime(2030, 1, 7, 9), datetime(2030, 1, 7, 9, 30), 100),    # started hour counts
        (datetime(2030, 1, 7, 9), datetime(2030, 1, 9, 10), 1700),      # 2 days + 1 h
        (datetime(2030, 1, 7, 8), datetime(2030, 1, 7, 20), 800),       # 12 h capped at a day
        (datetime(2030, 1, 7, 9), datetime(2030, 1, 8, 19), 1600),      # 1 day + 10 h (capped)
    ],
)
def test_calculate_price(start, end, expected):
    assert calculate_price(800, 100, start, end) == expected


# --- opening hours -----------------------------------------------------------------
def test_check_dates_accepts_valid_period():
    check_dates(START, END, now=datetime(2030, 1, 7, 7, 0))


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (END, START),                                              # return before pickup
        (START, START),                                            # zero length
        (datetime(2030, 1, 7, 7, 59), END),                        # before 08:00
        (START, datetime(2030, 1, 9, 20, 1)),                      # after 20:00
        (datetime(2030, 1, 5, 10, 0), END),                        # Saturday pickup
        (START, datetime(2030, 1, 13, 10, 0)),                     # Sunday return
    ],
)
def test_check_dates_rejects(start, end):
    with pytest.raises(Unprocessable):
        check_dates(start, end)


# --- notifications -------------------------------------------------------------------
def _confirmed_reservation() -> Reservation:
    car = Car(brand="Škoda", model="Fabia", license_plate="1AB 0001", daily_price=800,
              hourly_price=100, branch=Branch(name="B", address=""))
    user = User(name="Eva", email="eva@test.cz", password_hash="x", role="CUSTOMER")
    r = _reservation(car=car, user=user, status="CONFIRMED")
    r.id = 42
    r.total_price = 1700
    return r


def test_notification_implementation_is_chosen_by_smtp_host():
    assert isinstance(create_notification_service(Settings()), LoggingNotificationService)
    assert isinstance(create_notification_service(Settings(smtp_host="smtp.example.org")),
                      EmailNotificationService)


def test_logging_notification_returns_true(caplog):
    r = _confirmed_reservation()
    with caplog.at_level("INFO"):
        assert LoggingNotificationService().send_confirmation(r, r.user) is True
    assert "eva@test.cz" in caplog.text


class FakeSMTP:
    sent: list = []
    fail = False

    def __init__(self, host, port, timeout=None):
        self.host, self.port = host, port

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, message):
        if FakeSMTP.fail:
            raise OSError("connection refused")
        FakeSMTP.sent.append(message)


def test_email_notification_composes_and_sends():
    FakeSMTP.sent, FakeSMTP.fail = [], False
    service = EmailNotificationService(Settings(smtp_host="smtp.test", smtp_user="u"),
                                       smtp_factory=FakeSMTP)
    r = _confirmed_reservation()
    assert service.send_confirmation(r, r.user) is True
    message = FakeSMTP.sent[0]
    assert message["To"] == "eva@test.cz"
    assert "42" in message["Subject"]
    body = message.get_content()
    assert "07.01.2030 09:00" in body and "1700.00" in body


def test_email_failure_is_logged_and_returns_false(caplog):
    FakeSMTP.sent, FakeSMTP.fail = [], True
    service = EmailNotificationService(Settings(smtp_host="smtp.test"), smtp_factory=FakeSMTP)
    r = _confirmed_reservation()
    assert service.send_confirmation(r, r.user) is False
    assert r.status == "CONFIRMED"
    assert "failed" in caplog.text
