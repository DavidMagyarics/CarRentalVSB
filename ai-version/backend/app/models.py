"""Domain / ORM model (class-system.puml + er-current.puml)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import bcrypt
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .states import ReservationState, ReservationStatus, state_for


class UserRole:
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class PaymentMethod:
    CASH = "CASH"
    CARD = "CARD"


class Branch(Base):
    __tablename__ = "branch"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(String(255), default="")

    cars: Mapped[list["Car"]] = relationship(back_populates="branch")

    def get_name(self) -> str:
        return self.name


class Car(Base):
    __tablename__ = "car"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(80))
    year: Mapped[int] = mapped_column(Integer)
    license_plate: Mapped[str] = mapped_column(String(20), unique=True)
    daily_price: Mapped[float] = mapped_column(Float)
    hourly_price: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(40))
    transmission: Mapped[str] = mapped_column(String(40))
    fuel_type: Mapped[str] = mapped_column(String(40))
    seats: Mapped[int] = mapped_column(Integer, default=5)
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(500), default="")
    branch_id: Mapped[int] = mapped_column(ForeignKey("branch.id"))

    branch: Mapped[Branch] = relationship(back_populates="cars")
    # UC9: deleting a car deletes all its reservations together with it.
    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="car", cascade="all, delete-orphan", passive_deletes=True
    )

    UPDATABLE_FIELDS = (
        "brand", "model", "year", "license_plate", "daily_price", "hourly_price",
        "category", "transmission", "fuel_type", "seats", "description",
        "image_url", "branch_id",
    )

    def get_prices(self) -> tuple[float, float]:
        return self.daily_price, self.hourly_price

    def matches(self, filters: dict[str, Any]) -> bool:
        """True when the car satisfies every filter that is set (UC3)."""
        for attr in ("category", "transmission", "fuel_type"):
            wanted = filters.get(attr)
            if wanted and getattr(self, attr).lower() != str(wanted).lower():
                return False
        branch_id = filters.get("branch_id")
        if branch_id is not None and self.branch_id != branch_id:
            return False
        min_price = filters.get("min_price")
        if min_price is not None and self.daily_price < min_price:
            return False
        max_price = filters.get("max_price")
        if max_price is not None and self.daily_price > max_price:
            return False
        return True

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if key in self.UPDATABLE_FIELDS:
                setattr(self, key, value)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.CUSTOMER)

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="user",
        order_by="(Reservation.created_at.desc(), Reservation.id.desc())",
    )

    def check_password(self, password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
        except ValueError:
            return False

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def get_reservations(self) -> list["Reservation"]:
        """Reservations of this user, newest first (UC6)."""
        return list(self.reservations)


class Reservation(Base):
    """Context of the State pattern (pattern-state.puml)."""

    __tablename__ = "reservation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("car.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default=ReservationStatus.DRAFT)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    total_price: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    car: Mapped[Car] = relationship(back_populates="reservations")
    user: Mapped[User] = relationship(back_populates="reservations")

    def __init__(self, **kwargs: Any):
        # A new reservation always starts in DraftState.
        kwargs.setdefault("status", ReservationStatus.DRAFT)
        super().__init__(**kwargs)

    # --- State pattern -----------------------------------------------------
    @property
    def state(self) -> ReservationState:
        return state_for(self)

    def set_state(self, state: ReservationState) -> None:
        self.status = state.status

    def confirm(self, car_available: bool = True) -> None:
        self.state.confirm(car_available)

    def cancel(self, now: datetime | None = None) -> None:
        self.state.cancel(now)

    def blocks_car(self) -> bool:
        return self.state.blocks_car()

    # --- other operations from the class diagram ---------------------------
    def get_status(self) -> str:
        return self.status

    def get_user(self) -> User:
        return self.user

    def get_car(self) -> Car:
        return self.car

    def overlaps(self, start: datetime, end: datetime) -> bool:
        """Half-open interval overlap: existing start < requested end and existing end > requested start."""
        return self.start_date < end and self.end_date > start

    def rental_started(self, now: datetime | None = None) -> bool:
        """True in the "Rental started" sub-state of CONFIRMED."""
        now = now or datetime.now()
        return self.status == ReservationStatus.CONFIRMED and now >= self.start_date
