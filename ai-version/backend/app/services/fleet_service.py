"""FleetService - UC3 Browse & filter cars, UC9 Manage fleet."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..errors import (
    MSG_ADMIN_REQUIRED,
    MSG_BRANCH_NOT_FOUND,
    MSG_CAR_NOT_FOUND,
    MSG_CATEGORY_IN_USE,
    MSG_CATEGORY_NOT_FOUND,
    MSG_CATEGORY_TAKEN,
    MSG_PLATE_TAKEN,
    MSG_UNKNOWN_CATEGORY,
    Conflict,
    Forbidden,
    NotFound,
    Unprocessable,
)
from ..models import Branch, Car, CarCategory, User


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

    # --- Car categories (version 2.0) ----------------------------------------
    def get_categories(self) -> list[CarCategory]:
        return list(self.db.scalars(select(CarCategory).order_by(CarCategory.name)))

    def create_category(self, user: User, name: str) -> CarCategory:
        self._require_admin(user)
        if self._find_category(name) is not None:
            raise Conflict(MSG_CATEGORY_TAKEN)
        category = CarCategory(name=name)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, user: User, category_id: int) -> None:
        self._require_admin(user)
        category = self.db.get(CarCategory, category_id)
        if category is None:
            raise NotFound(MSG_CATEGORY_NOT_FOUND)
        if self.db.scalar(select(Car.id).where(Car.category == category.name).limit(1)):
            raise Conflict(MSG_CATEGORY_IN_USE)
        self.db.delete(category)
        self.db.commit()

    # --- UC9 ------------------------------------------------------------------
    def create_car(self, user: User, data: dict[str, Any]) -> Car:
        self._require_admin(user)
        data["category"] = self._check_category(data["category"])
        branch = self.get_branch(data["branch_id"])
        car = Car(**{k: v for k, v in data.items() if k != "branch_id"}, branch=branch)
        self.db.add(car)
        self._commit()
        self.db.refresh(car)
        return car

    def update_car(self, user: User, car_id: int, data: dict[str, Any]) -> Car:
        self._require_admin(user)
        car = self.get_car(car_id)
        if data.get("category") is not None:
            data["category"] = self._check_category(data["category"])
        if data.get("branch_id") is not None:
            self.get_branch(data["branch_id"])
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

    def _find_category(self, name: str) -> CarCategory | None:
        return self.db.scalar(select(CarCategory).where(CarCategory.name.ilike(name)))

    def _check_category(self, name: str) -> str:
        """The category's stored name (its exact spelling), or 422 when it doesn't exist."""
        category = self._find_category(name)
        if category is None:
            raise Unprocessable(MSG_UNKNOWN_CATEGORY)
        return category.name

    @staticmethod
    def _require_admin(user: User) -> None:
        if not user.is_admin():
            raise Forbidden(MSG_ADMIN_REQUIRED)

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise Conflict(MSG_PLATE_TAKEN) from exc
