from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..notification import notification_service

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
            detail="Auto je v požadovaném termínu již potvrzenou rezervací obsazeno",
        )

    return crud.create_reservation(db, reservation)


@router.post("/{reservation_id}/confirm", response_model=schemas.Reservation)
def confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    try:
        reservation = crud.confirm_reservation(db, reservation_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except crud.DomainError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    user = db.query(models.User).filter(models.User.id == reservation.user_id).first()
    notification_service.send_confirmation(reservation, user)
    return reservation


@router.post("/{reservation_id}/cancel", response_model=schemas.Reservation)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    try:
        return crud.cancel_reservation(db, reservation_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except crud.DomainError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
