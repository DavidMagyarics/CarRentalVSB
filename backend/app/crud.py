from datetime import UTC, datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from . import models, schemas


class DomainError(Exception):
    """Raised when an operation violates a domain/business rule."""


def get_cars(db: Session) -> list[models.Car]:
    return db.query(models.Car).all()


def get_car(db: Session, car_id: int) -> models.Car | None:
    return db.query(models.Car).filter(models.Car.id == car_id).first()


def create_car(db: Session, car: schemas.CarCreate) -> models.Car:
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


def get_or_create_user(db: Session, name: str, email: str) -> models.User:
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is not None:
        return user
    user = models.User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


def is_car_available(db: Session, car_id: int, start_date, end_date) -> bool:
    """A car is available in a slot if no CONFIRMED reservation overlaps it.

    This is the common business rule: two CONFIRMED reservations for the
    same resource must never overlap. DRAFT reservations do not block the
    slot yet — they only become binding once confirmed.
    """
    overlapping = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.car_id == car_id,
            models.Reservation.status == models.ReservationStatus.CONFIRMED,
            and_(
                models.Reservation.start_date < end_date,
                models.Reservation.end_date > start_date,
            ),
        )
        .first()
    )
    return overlapping is None


def get_reservations(db: Session) -> list[models.Reservation]:
    return db.query(models.Reservation).all()


def get_reservation(db: Session, reservation_id: int) -> models.Reservation | None:
    return (
        db.query(models.Reservation)
        .filter(models.Reservation.id == reservation_id)
        .first()
    )


def create_reservation(
    db: Session, reservation: schemas.ReservationCreate
) -> models.Reservation:
    user = get_or_create_user(db, reservation.customer_name, reservation.customer_email)
    db_reservation = models.Reservation(
        car_id=reservation.car_id,
        user_id=user.id,
        start_date=reservation.start_date,
        end_date=reservation.end_date,
        status=models.ReservationStatus.DRAFT,
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def confirm_reservation(db: Session, reservation_id: int) -> models.Reservation:
    reservation = get_reservation(db, reservation_id)
    if reservation is None:
        raise LookupError("Rezervace nenalezena")

    if reservation.status != models.ReservationStatus.DRAFT:
        raise DomainError(
            f"Rezervaci ve stavu {reservation.status.value} nelze potvrdit"
        )

    if not is_car_available(
        db, reservation.car_id, reservation.start_date, reservation.end_date
    ):
        raise DomainError("Auto je v tomto termínu už jinou rezervací potvrzeno")

    reservation.status = models.ReservationStatus.CONFIRMED
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation_id: int) -> models.Reservation:
    reservation = get_reservation(db, reservation_id)
    if reservation is None:
        raise LookupError("Rezervace nenalezena")

    if reservation.status == models.ReservationStatus.CANCELLED:
        raise DomainError("Rezervace je již zrušena")

    # Domain-specific business rule: a reservation whose rental period has
    # already started can no longer be cancelled through the system.
    now = datetime.now(UTC)
    start = reservation.start_date
    if start.tzinfo is None:
        now = now.replace(tzinfo=None)
    if reservation.status == models.ReservationStatus.CONFIRMED and start <= now:
        raise DomainError(
            "Potvrzenou rezervaci nelze zrušit poté, co již začal termín výpůjčky"
        )

    reservation.status = models.ReservationStatus.CANCELLED
    db.commit()
    db.refresh(reservation)
    return reservation
