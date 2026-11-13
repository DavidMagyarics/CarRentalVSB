"""FleetService - UC3 Browse & filter cars, UC9 Manage fleet."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..errors import MSG_HOURLY_ABOVE_DAILY, Unprocessable

from ..errors import (
    MSG_ADMIN_REQUIRED,
    MSG_BRANCH_NOT_FOUND,
    MSG_CAR_NOT_FOUND,
    MSG_PLATE_TAKEN,
    Conflict,
    Forbidden,
    NotFound,
)
from ..models import Branch, Car, User


class FleetService:
    def __init__(self, db: Session):
        self.db = db

    # --- UC3 ------------------------------------------------------------------
    def get_cars(self, filters: dict[str, Any] | None = None) -> list[Car]:
        """No filter set = every car; otherwise every car for which c.matches(filters)."""
        filters = {k: v for k, v in (filters or {}).items() if v not in (None, "")}
        cars = self.db.scalars(
            select(Car).options(selectinload(Car.branch)).order_by(Car.id)
        )
        return [car for car in cars if car.matches(filters)]

    def get_branches(self) -> list[Branch]:
        return list(self.db.scalars(select(Branch).order_by(Branch.id)))

    # --- UC9 ------------------------------------------------------------------
    def create_car(self, user: User, data: dict[str, Any]) -> Car:
        self._require_admin(user)
        branch = self.get_branch(data["branch_id"])
        car = Car(**{k: v for k, v in data.items() if k != "branch_id"}, branch=branch)
        self._check_prices(car.daily_price, car.hourly_price)
        self.db.add(car)
        self._commit()
        self.db.refresh(car)
        return car

    def update_car(self, user: User, car_id: int, data: dict[str, Any]) -> Car:
        self._require_admin(user)
        car = self.get_car(car_id)
        if data.get("branch_id") is not None:
            self.get_branch(data["branch_id"])
        self._check_prices(
            data.get("daily_price") or car.daily_price, data.get("hourly_price") or car.hourly_price
        )
        car.update({k: v for k, v in data.items() if v is not None})
        self._commit()
        self.db.refresh(car)
        return car

    def delete_car(self, user: User, car_id: int) -> None:
        """Deletes the car together with all its reservations."""
        self._require_admin(user)
        car = self.get_car(car_id)
        self.db.delete(car)
        self.db.commit()

    # --- private --------------------------------------------------------------
    def get_car(self, car_id: int) -> Car:
        car = self.db.get(Car, car_id)
        if car is None:
            raise NotFound(MSG_CAR_NOT_FOUND)
        return car

    def get_branch(self, branch_id: int) -> Branch:
        branch = self.db.get(Branch, branch_id)
        if branch is None:
            raise NotFound(MSG_BRANCH_NOT_FOUND)
        return branch

    @staticmethod
    def _require_admin(user: User) -> None:
        if not user.is_admin():
            raise Forbidden(MSG_ADMIN_REQUIRED)

    @staticmethod
    def _check_prices(daily_price: float, hourly_price: float) -> None:
        """An hour may never cost more than a whole day."""
        if hourly_price > daily_price:
            raise Unprocessable(MSG_HOURLY_ABOVE_DAILY)

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise Conflict(MSG_PLATE_TAKEN) from exc
