"""ReservationService - UC4, UC4a, UC5, UC6, UC8 (+UC8a), UC10."""

from __future__ import annotations

import math
from datetime import datetime, time, timedelta
from typing import Callable

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from ..errors import (
    MSG_ADMIN_REQUIRED,
    MSG_CAR_NOT_FOUND,
    MSG_NOT_YOUR_RESERVATION,
    MSG_OPENING_HOURS,
    MSG_PICKUP_IN_PAST,
    MSG_RESERVATION_NOT_FOUND,
    MSG_RETURN_BEFORE_PICKUP,
    MSG_SLOT_TAKEN_ON_CREATE,
    Conflict,
    Forbidden,
    NotFound,
    Unprocessable,
)
from ..models import Car, Reservation, User
from ..states import BLOCKING_STATUSES, ReservationStatus
from .notification import NotificationService

# Opening hours: Mon-Fri, 08:00-20:00 (activity-make-reservation.puml)
OPENING_TIME = time(8, 0)
CLOSING_TIME = time(20, 0)
WORKING_DAYS = range(0, 5)  # Monday=0 ... Friday=4


def normalize(dt: datetime) -> datetime:
    """Store everything as naive local time (an aware value is converted first)."""
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt.replace(microsecond=0)


def within_opening_hours(dt: datetime) -> bool:
    return dt.weekday() in WORKING_DAYS and OPENING_TIME <= dt.time() <= CLOSING_TIME


def check_dates(start: datetime, end: datetime, now: datetime | None = None) -> None:
    """Raise 422 unless return is after pickup and both are within opening hours."""
    if end <= start:
        raise Unprocessable(MSG_RETURN_BEFORE_PICKUP)
    if not (within_opening_hours(start) and within_opening_hours(end)):
        raise Unprocessable(MSG_OPENING_HOURS)
    if now is not None and start < now:
        raise Unprocessable(MSG_PICKUP_IN_PAST)


def calculate_price(daily_price: float, hourly_price: float, start: datetime, end: datetime) -> float:
    """Daily rate per full 24 h block + hourly rate for the rest (started hours),
    the rest capped at one more day's rate."""
    duration = end - start
    full_days = duration // timedelta(days=1)
    rest = duration - timedelta(days=full_days)
    rest_hours = math.ceil(rest.total_seconds() / 3600)
    rest_price = min(rest_hours * hourly_price, daily_price) if rest_hours else 0.0
    return round(full_days * daily_price + rest_price, 2)


class ReservationService:
    def __init__(
        self,
        db: Session,
        notifier: NotificationService,
        clock: Callable[[], datetime] = datetime.now,
    ):
        self.db = db
        self.notifier = notifier
        self.clock = clock

    # --- UC4 ----------------------------------------------------------------
    def create_reservation(
        self, user: User, car_id: int, start: datetime, end: datetime, payment_method: str
    ) -> Reservation:
        start, end = normalize(start), normalize(end)
        car = self.db.get(Car, car_id)
        if car is None:
            raise NotFound(MSG_CAR_NOT_FOUND)
        # The server checks everything again - the request may not come from the form.
        check_dates(start, end, now=self.clock())
        if not self.is_car_available(car.id, start, end):
            raise Conflict(MSG_SLOT_TAKEN_ON_CREATE)
        reservation = Reservation(
            car=car,
            user=user,
            start_date=start,
            end_date=end,
            total_price=self.calculate_price(car, start, end),
            payment_method=payment_method,
            status=ReservationStatus.DRAFT,
            created_at=self.clock(),
        )
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    # --- UC4a ---------------------------------------------------------------
    def is_car_available(self, car_id: int, start: datetime, end: datetime) -> bool:
        """Only reservations whose state blocks the car (CONFIRMED) are checked.
        Overlap: existing start < requested end and existing end > requested start."""
        start, end = normalize(start), normalize(end)
        overlapping = exists().where(
            Reservation.car_id == car_id,
            Reservation.status.in_(BLOCKING_STATUSES),
            Reservation.start_date < end,
            Reservation.end_date > start,
        )
        return not self.db.scalar(select(overlapping))

    # --- UC8 (+UC8a) --------------------------------------------------------
    def confirm_reservation(self, user: User, reservation_id: int) -> Reservation:
        if not user.is_admin():
            raise Forbidden(MSG_ADMIN_REQUIRED)
        reservation = self.get_reservation(reservation_id)
        car_available = True
        if reservation.get_status() == ReservationStatus.DRAFT:
            car_available = self.is_car_available(
                reservation.car_id, reservation.start_date, reservation.end_date
            )
        # State pattern: Draft -> Confirmed, or 409 from the current state.
        reservation.confirm(car_available)
        self.db.commit()
        self.db.refresh(reservation)
        # entry / send_confirmation(r, user) - a failure is only logged.
        self.notifier.send_confirmation(reservation, reservation.get_user())
        return reservation

    # --- UC5 ----------------------------------------------------------------
    def cancel_reservation(self, user: User, reservation_id: int) -> Reservation:
        reservation = self.get_reservation(reservation_id)
        if reservation.get_user().id != user.id and not user.is_admin():
            raise Forbidden(MSG_NOT_YOUR_RESERVATION)
        reservation.cancel(now=self.clock())
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    # --- UC6 / UC10 -----------------------------------------------------------
    def get_reservations_for_user(self, user: User) -> list[Reservation]:
        return user.get_reservations()

    def get_reservations(self, user: User) -> list[Reservation]:
        if not user.is_admin():
            raise Forbidden(MSG_ADMIN_REQUIRED)
        stmt = (
            select(Reservation)
            .options(selectinload(Reservation.car), selectinload(Reservation.user))
            .order_by(Reservation.created_at.desc(), Reservation.id.desc())
        )
        return list(self.db.scalars(stmt))

    # --- private --------------------------------------------------------------
    def get_reservation(self, reservation_id: int) -> Reservation:
        reservation = self.db.get(Reservation, reservation_id)
        if reservation is None:
            raise NotFound(MSG_RESERVATION_NOT_FOUND)
        return reservation

    @staticmethod
    def calculate_price(car: Car, start: datetime, end: datetime) -> float:
        daily, hourly = car.get_prices()
        return calculate_price(daily, hourly, start, end)
