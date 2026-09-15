from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


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


class ReservationBase(BaseModel):
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


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
