from sqlalchemy import and_
from sqlalchemy.orm import Session

from . import models, schemas


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


def is_car_available(
    db: Session, car_id: int, start_date, end_date
) -> bool:
    """Auto je volné, pokud se požadovaný termín nepřekrývá s žádnou existující rezervací."""
    overlapping = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.car_id == car_id,
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


def create_reservation(
    db: Session, reservation: schemas.ReservationCreate
) -> models.Reservation:
    db_reservation = models.Reservation(**reservation.model_dump())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation
