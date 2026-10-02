import math
from datetime import UTC, datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from . import auth, models, schemas


class DomainError(Exception):
    """Raised when an operation violates a domain/business rule."""


def get_branches(db: Session) -> list[models.Branch]:
    return db.query(models.Branch).order_by(models.Branch.name).all()


def get_branch(db: Session, branch_id: int) -> models.Branch | None:
    return db.query(models.Branch).filter(models.Branch.id == branch_id).first()


def create_branch(db: Session, branch: schemas.BranchCreate) -> models.Branch:
    db_branch = models.Branch(**branch.model_dump())
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch


def update_branch(
    db: Session, branch_id: int, branch: schemas.BranchUpdate
) -> models.Branch | None:
    db_branch = get_branch(db, branch_id)
    if db_branch is None:
        return None
    for field, value in branch.model_dump(exclude_unset=True).items():
        setattr(db_branch, field, value)
    db.commit()
    db.refresh(db_branch)
    return db_branch


def delete_branch(db: Session, branch_id: int) -> bool:
    db_branch = get_branch(db, branch_id)
    if db_branch is None:
        return False
    if db_branch.cars:
        raise DomainError(
            "Pobočku nelze smazat, dokud k ní jsou přiřazená auta"
        )
    db.delete(db_branch)
    db.commit()
    return True


def calculate_price(car: models.Car, start_date: datetime, end_date: datetime) -> float:
    """Whole days cost the daily rate; the leftover hours are billed at the
    hourly rate but never more than another full day — so booking close to
    a full day (or several) is never worse than booking it by the hour."""
    total_hours = math.ceil((end_date - start_date).total_seconds() / 3600)
    full_days, remaining_hours = divmod(total_hours, 24)
    remaining_price = min(remaining_hours * car.hourly_price, car.daily_price) if remaining_hours else 0
    return full_days * car.daily_price + remaining_price


def get_cars(
    db: Session,
    category: models.CarCategory | None = None,
    transmission: models.Transmission | None = None,
    fuel_type: models.FuelType | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_seats: int | None = None,
    branch_id: int | None = None,
) -> list[models.Car]:
    query = db.query(models.Car)
    if category is not None:
        query = query.filter(models.Car.category == category)
    if transmission is not None:
        query = query.filter(models.Car.transmission == transmission)
    if fuel_type is not None:
        query = query.filter(models.Car.fuel_type == fuel_type)
    if min_price is not None:
        query = query.filter(models.Car.daily_price >= min_price)
    if max_price is not None:
        query = query.filter(models.Car.daily_price <= max_price)
    if min_seats is not None:
        query = query.filter(models.Car.seats >= min_seats)
    if branch_id is not None:
        query = query.filter(models.Car.branch_id == branch_id)
    return query.order_by(models.Car.brand, models.Car.model).all()


def get_car(db: Session, car_id: int) -> models.Car | None:
    return db.query(models.Car).filter(models.Car.id == car_id).first()


def create_car(db: Session, car: schemas.CarCreate) -> models.Car:
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


def update_car(db: Session, car_id: int, car: schemas.CarUpdate) -> models.Car | None:
    db_car = get_car(db, car_id)
    if db_car is None:
        return None
    for field, value in car.model_dump(exclude_unset=True).items():
        setattr(db_car, field, value)
    db.commit()
    db.refresh(db_car)
    return db_car


def delete_car(db: Session, car_id: int) -> bool:
    db_car = get_car(db, car_id)
    if db_car is None:
        return False
    db.delete(db_car)
    db.commit()
    return True


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: models.UserRole = models.UserRole.CUSTOMER,
) -> models.User:
    user = models.User(
        name=name, email=email, password_hash=auth.hash_password(password), role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = get_user_by_email(db, email)
    if user is None or not auth.verify_password(password, user.password_hash):
        return None
    return user


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
    return db.query(models.Reservation).order_by(models.Reservation.id.desc()).all()


def get_reservations_for_user(db: Session, user_id: int) -> list[models.Reservation]:
    return (
        db.query(models.Reservation)
        .filter(models.Reservation.user_id == user_id)
        .order_by(models.Reservation.id.desc())
        .all()
    )


def get_reservation(db: Session, reservation_id: int) -> models.Reservation | None:
    return (
        db.query(models.Reservation)
        .filter(models.Reservation.id == reservation_id)
        .first()
    )


def create_reservation(
    db: Session, user_id: int, car: models.Car, reservation: schemas.ReservationCreate
) -> models.Reservation:
    db_reservation = models.Reservation(
        car_id=reservation.car_id,
        user_id=user_id,
        start_date=reservation.start_date,
        end_date=reservation.end_date,
        status=models.ReservationStatus.DRAFT,
        total_price=calculate_price(car, reservation.start_date, reservation.end_date),
        payment_method=reservation.payment_method,
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
