"""Pydantic request / response schemas (HTTP/JSON contract)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PaymentMethodLiteral = Literal["CASH", "CARD"]


# --- auth --------------------------------------------------------------------
class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Jméno nesmí být prázdné")
        return value


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- branches / cars ---------------------------------------------------------
class BranchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str


class CarBase(BaseModel):
    brand: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1950, le=2100)
    license_plate: str = Field(min_length=1, max_length=20)
    daily_price: float = Field(gt=0)
    hourly_price: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=40)
    transmission: str = Field(min_length=1, max_length=40)
    fuel_type: str = Field(min_length=1, max_length=40)
    seats: int = Field(default=5, ge=1, le=60)
    description: str = ""
    image_url: str = ""
    branch_id: int


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=80)
    year: int | None = Field(default=None, ge=1950, le=2100)
    license_plate: str | None = Field(default=None, min_length=1, max_length=20)
    daily_price: float | None = Field(default=None, gt=0)
    hourly_price: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=40)
    transmission: str | None = Field(default=None, min_length=1, max_length=40)
    fuel_type: str | None = Field(default=None, min_length=1, max_length=40)
    seats: int | None = Field(default=None, ge=1, le=60)
    description: str | None = None
    image_url: str | None = None
    branch_id: int | None = None


class CarOut(CarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    branch: BranchOut


class AvailabilityOut(BaseModel):
    car_id: int
    start_date: datetime
    end_date: datetime
    available: bool


# --- reservations ------------------------------------------------------------
class ReservationCreate(BaseModel):
    car_id: int
    start_date: datetime
    end_date: datetime
    payment_method: PaymentMethodLiteral


class CarSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    license_plate: str
    image_url: str
    branch_id: int


class ReservationOut(BaseModel):
    id: int
    car_id: int
    user_id: int
    status: str
    start_date: datetime
    end_date: datetime
    total_price: float
    payment_method: str
    created_at: datetime
    rental_started: bool
    car: CarSummary
    user: UserOut
