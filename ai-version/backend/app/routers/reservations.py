from __future__ import annotations

from datetime import datetime
from typing import Annotated, Callable

from fastapi import APIRouter, Depends, status

from ..deps import CurrentUser, ReservationServiceDep, get_clock
from ..models import Reservation
from ..schemas import CarSummary, ReservationCreate, ReservationOut, UserOut

router = APIRouter(prefix="/reservations", tags=["reservations"])

ClockDep = Annotated[Callable[[], datetime], Depends(get_clock)]


def to_out(reservation: Reservation, now: datetime) -> ReservationOut:
    return ReservationOut(
        id=reservation.id,
        car_id=reservation.car_id,
        user_id=reservation.user_id,
        status=reservation.status,
        start_date=reservation.start_date,
        end_date=reservation.end_date,
        total_price=reservation.total_price,
        payment_method=reservation.payment_method,
        created_at=reservation.created_at,
        rental_started=reservation.rental_started(now),
        car=CarSummary.model_validate(reservation.car),
        user=UserOut.model_validate(reservation.user),
    )


@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    body: ReservationCreate, user: CurrentUser, service: ReservationServiceDep, clock: ClockDep
):
    """UC4 - 201 DRAFT; 404 unknown car; 409 slot taken; 422 invalid dates."""
    reservation = service.create_reservation(
        user, body.car_id, body.start_date, body.end_date, body.payment_method
    )
    return to_out(reservation, clock())


@router.get("/me", response_model=list[ReservationOut])
def my_reservations(user: CurrentUser, service: ReservationServiceDep, clock: ClockDep):
    """UC6 - reservations of the logged-in user, newest first; 401 without a valid token."""
    now = clock()
    return [to_out(r, now) for r in service.get_reservations_for_user(user)]


@router.get("/", response_model=list[ReservationOut])
def all_reservations(user: CurrentUser, service: ReservationServiceDep, clock: ClockDep):
    """UC10 - every reservation, newest first; 403 for non-admins."""
    now = clock()
    return [to_out(r, now) for r in service.get_reservations(user)]


@router.post("/{reservation_id}/confirm", response_model=ReservationOut)
def confirm_reservation(
    reservation_id: int, user: CurrentUser, service: ReservationServiceDep, clock: ClockDep
):
    """UC8 - 200; 403 non-admin; 404; 409 not DRAFT or slot taken."""
    return to_out(service.confirm_reservation(user, reservation_id), clock())


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(
    reservation_id: int, user: CurrentUser, service: ReservationServiceDep, clock: ClockDep
):
    """UC5 - 200; 403 not yours; 404; 409 already cancelled / rental started."""
    return to_out(service.cancel_reservation(user, reservation_id), clock())
