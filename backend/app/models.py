import enum
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class ReservationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class CarCategory(str, enum.Enum):
    SEDAN = "SEDAN"
    SUV = "SUV"
    HATCHBACK = "HATCHBACK"
    VAN = "VAN"
    SPORTS = "SPORTS"


class Transmission(str, enum.Enum):
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"


class FuelType(str, enum.Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    ELECTRIC = "ELECTRIC"
    HYBRID = "HYBRID"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)

    reservations = relationship("Reservation", back_populates="user")


class Branch(Base):
    """A physical rental location a car can be picked up from and returned
    to (F11). Every car belongs to exactly one branch — there is no
    cross-branch drop-off yet, see docs/domain-model.md."""

    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    cars = relationship("Car", back_populates="branch")


class Car(Base):
    """The reservation Resource: a car available in the fleet."""

    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    license_plate = Column(String, unique=True, nullable=False)
    daily_price = Column(Float, nullable=False)
    hourly_price = Column(Float, nullable=False)
    category = Column(Enum(CarCategory), nullable=False, default=CarCategory.SEDAN)
    transmission = Column(Enum(Transmission), nullable=False, default=Transmission.MANUAL)
    fuel_type = Column(Enum(FuelType), nullable=False, default=FuelType.PETROL)
    seats = Column(Integer, nullable=False, default=5)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    branch = relationship("Branch", back_populates="cars")
    reservations = relationship(
        "Reservation", back_populates="car", cascade="all, delete-orphan"
    )


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum(ReservationStatus), nullable=False, default=ReservationStatus.DRAFT
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_price = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False, default=PaymentMethod.CASH)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    car = relationship("Car", back_populates="reservations")
    user = relationship("User", back_populates="reservations")
