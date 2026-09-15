from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/", response_model=list[schemas.Reservation])
def list_reservations(db: Session = Depends(get_db)):
    return crud.get_reservations(db)


@router.post("/", response_model=schemas.Reservation, status_code=201)
def create_reservation(
    reservation: schemas.ReservationCreate, db: Session = Depends(get_db)
):
    car = crud.get_car(db, reservation.car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Auto nenalezeno")

    if not crud.is_car_available(
        db, reservation.car_id, reservation.start_date, reservation.end_date
    ):
        raise HTTPException(
            status_code=409,
            detail="Auto je v požadovaném termínu již rezervováno",
        )

    return crud.create_reservation(db, reservation)
