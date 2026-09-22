from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..deps import require_admin

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/", response_model=list[schemas.Car])
def list_cars(
    category: models.CarCategory | None = None,
    transmission: models.Transmission | None = None,
    fuel_type: models.FuelType | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_seats: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_cars(
        db,
        category=category,
        transmission=transmission,
        fuel_type=fuel_type,
        min_price=min_price,
        max_price=max_price,
        min_seats=min_seats,
    )


@router.get("/{car_id}", response_model=schemas.Car)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = crud.get_car(db, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Auto nenalezeno")
    return car


@router.post("/", response_model=schemas.Car, status_code=201)
def create_car(
    car: schemas.CarCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    return crud.create_car(db, car)


@router.put("/{car_id}", response_model=schemas.Car)
def update_car(
    car_id: int,
    car: schemas.CarUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    updated = crud.update_car(db, car_id, car)
    if updated is None:
        raise HTTPException(status_code=404, detail="Auto nenalezeno")
    return updated


@router.delete("/{car_id}", status_code=204)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    if not crud.delete_car(db, car_id):
        raise HTTPException(status_code=404, detail="Auto nenalezeno")


@router.get("/{car_id}/availability", response_model=schemas.Availability)
def check_availability(
    car_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
):
    car = crud.get_car(db, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Auto nenalezeno")
    if end_date <= start_date:
        raise HTTPException(
            status_code=422, detail="end_date musí být později než start_date"
        )

    available = crud.is_car_available(db, car_id, start_date, end_date)
    return schemas.Availability(
        car_id=car_id, start_date=start_date, end_date=end_date, available=available
    )
