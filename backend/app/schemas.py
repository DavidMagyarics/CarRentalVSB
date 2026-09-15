from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from .models import ReservationStatus


class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    license_plate: str
    daily_price: float


class CarCreate(CarBase):
    pass


class Car(CarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class ReservationCreate(BaseModel):
    car_id: int
    customer_name: str
    customer_email: EmailStr
    start_date: datetime
    end_date: datetime

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, end_date: datetime, info):
        start_date = info.data.get("start_date")
        if start_date and end_date <= start_date:
            raise ValueError("end_date musí být později než start_date")
        return end_date


class Reservation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    car_id: int
    user_id: int
    status: ReservationStatus
    start_date: datetime
    end_date: datetime
    created_at: datetime


class Availability(BaseModel):
    car_id: int
    start_date: datetime
    end_date: datetime
    available: bool
