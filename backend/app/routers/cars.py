from fastapi import APIRouter, Depends, HTTPException
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
