from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .models import CarCategory, FuelType, ReservationStatus, Transmission, UserRole


class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    license_plate: str
    daily_price: float
    category: CarCategory = CarCategory.SEDAN
    transmission: Transmission = Transmission.MANUAL
    fuel_type: FuelType = FuelType.PETROL
    seats: int = Field(default=5, ge=1, le=9)
    description: str | None = None


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    license_plate: str | None = None
    daily_price: float | None = None
    category: CarCategory | None = None
    transmission: Transmission | None = None
    fuel_type: FuelType | None = None
    seats: int | None = Field(default=None, ge=1, le=9)
    description: str | None = None


class Car(CarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class ReservationCreate(BaseModel):
    car_id: int
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
    car: Car
    user: User


class Availability(BaseModel):
    car_id: int
    start_date: datetime
    end_date: datetime
    available: bool
