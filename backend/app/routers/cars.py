from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/", response_model=list[schemas.Car])
def list_cars(db: Session = Depends(get_db)):
    return crud.get_cars(db)


@router.get("/{car_id}", response_model=schemas.Car)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = crud.get_car(db, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Auto nenalezeno")
    return car


@router.post("/", response_model=schemas.Car, status_code=201)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    return crud.create_car(db, car)


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
