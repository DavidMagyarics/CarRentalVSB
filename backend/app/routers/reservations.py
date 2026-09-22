from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..deps import get_current_user, require_admin
from ..notification import notification_service

router = APIRouter(prefix="/reservations", tags=["reservations"])


def _ensure_owner_or_admin(reservation: models.Reservation, current_user: models.User) -> None:
    if current_user.role != models.UserRole.ADMIN and reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Tato rezervace vám nepatří")


@router.get("/", response_model=list[schemas.Reservation])
def list_all_reservations(
    db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    return crud.get_reservations(db)


@router.get("/me", response_model=list[schemas.Reservation])
def list_my_reservations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_reservations_for_user(db, current_user.id)


@router.post("/", response_model=schemas.Reservation, status_code=201)
def create_reservation(
    reservation: schemas.ReservationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
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

    return crud.create_reservation(db, current_user.id, reservation)


@router.post("/{reservation_id}/confirm", response_model=schemas.Reservation)
def confirm_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = crud.get_reservation(db, reservation_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Rezervace nenalezena")
    _ensure_owner_or_admin(existing, current_user)

    try:
        reservation = crud.confirm_reservation(db, reservation_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except crud.DomainError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    notification_service.send_confirmation(reservation, reservation.user)
    return reservation


@router.post("/{reservation_id}/cancel", response_model=schemas.Reservation)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = crud.get_reservation(db, reservation_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Rezervace nenalezena")
    _ensure_owner_or_admin(existing, current_user)

    try:
        return crud.cancel_reservation(db, reservation_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except crud.DomainError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
