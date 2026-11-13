from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query, Response, status

from ..deps import CurrentUser, FleetServiceDep, ReservationServiceDep
from ..errors import MSG_RETURN_BEFORE_PICKUP, Unprocessable
from ..schemas import AvailabilityOut, BranchOut, CarCreate, CarOut, CarUpdate
from ..services.reservation_service import normalize

router = APIRouter(tags=["cars"])


@router.get("/branches/", response_model=list[BranchOut])
def list_branches(fleet: FleetServiceDep):
    return fleet.get_branches()


@router.get("/cars/", response_model=list[CarOut])
def list_cars(
    fleet: FleetServiceDep,
    category: str | None = None,
    transmission: str | None = None,
    fuel_type: str | None = None,
    min_price: float | None = Query(default=None, ge=0, description="Minimum price per day"),
    max_price: float | None = Query(default=None, ge=0, description="Maximum price per day"),
    branch_id: int | None = None,
):
    """UC3 - no filter = every car; [] when nothing matches."""
    return fleet.get_cars(
        {
            "category": category,
            "transmission": transmission,
            "fuel_type": fuel_type,
            "min_price": min_price,
            "max_price": max_price,
            "branch_id": branch_id,
        }
    )


@router.get("/cars/{car_id}", response_model=CarOut)
def get_car(car_id: int, fleet: FleetServiceDep):
    return fleet.get_car(car_id)


@router.get("/cars/{car_id}/availability", response_model=AvailabilityOut)
def car_availability(
    car_id: int,
    start_date: datetime,
    end_date: datetime,
    fleet: FleetServiceDep,
    reservations: ReservationServiceDep,
):
    """UC4a - is the car free for [start_date, end_date)?"""
    car = fleet.get_car(car_id)
    start, end = normalize(start_date), normalize(end_date)
    if end <= start:
        raise Unprocessable(MSG_RETURN_BEFORE_PICKUP)
    return AvailabilityOut(
        car_id=car.id,
        start_date=start,
        end_date=end,
        available=reservations.is_car_available(car.id, start, end),
    )


@router.post("/cars/", response_model=CarOut, status_code=status.HTTP_201_CREATED)
def create_car(body: CarCreate, user: CurrentUser, fleet: FleetServiceDep):
    """UC9 Add - 201; 403 non-admin; 404 unknown branch."""
    return fleet.create_car(user, body.model_dump())


@router.put("/cars/{car_id}", response_model=CarOut)
def update_car(car_id: int, body: CarUpdate, user: CurrentUser, fleet: FleetServiceDep):
    """UC9 Edit - 200; 403 non-admin; 404 unknown car / branch."""
    return fleet.update_car(user, car_id, body.model_dump(exclude_unset=True))


@router.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int, user: CurrentUser, fleet: FleetServiceDep):
    """UC9 Delete - 204; the car's reservations are deleted with it."""
    fleet.delete_car(user, car_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
