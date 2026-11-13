"""Demo data inserted on first start (only into an empty database)."""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Branch, Car, User, UserRole
from .security import hash_password

logger = logging.getLogger("carrental.seed")

DEMO_ADMIN = {"name": "Admin Demo", "email": "admin@carrental.cz", "password": "admin123"}
DEMO_CUSTOMER = {"name": "Jan Novák", "email": "customer@carrental.cz", "password": "customer123"}

BRANCHES = [
    {"name": "Ostrava – centrum", "address": "Nádražní 12, 702 00 Ostrava"},
    {"name": "Ostrava – Poruba (VŠB)", "address": "17. listopadu 2172/15, 708 00 Ostrava-Poruba"},
    {"name": "Praha – Letiště", "address": "Aviatická 1017/2, 161 00 Praha 6"},
]

CARS = [
    dict(brand="Škoda", model="Fabia", year=2022, license_plate="8T1 2345", daily_price=790, hourly_price=90,
         category="Hatchback", transmission="Manual", fuel_type="Petrol", seats=5,
         description="Úsporné auto do města.", branch=0),
    dict(brand="Škoda", model="Octavia Combi", year=2023, license_plate="8T2 1111", daily_price=1190, hourly_price=140,
         category="Combi", transmission="Automatic", fuel_type="Diesel", seats=5,
         description="Prostorné kombi na dovolenou.", branch=0),
    dict(brand="Hyundai", model="Tucson", year=2023, license_plate="8T3 4567", daily_price=1490, hourly_price=170,
         category="SUV", transmission="Automatic", fuel_type="Hybrid", seats=5,
         description="Pohodlné SUV s hybridním pohonem.", branch=1),
    dict(brand="Tesla", model="Model 3", year=2024, license_plate="8T4 0001", daily_price=1990, hourly_price=230,
         category="Sedan", transmission="Automatic", fuel_type="Electric", seats=5,
         description="Elektromobil s dojezdem přes 500 km.", branch=2),
    dict(brand="Ford", model="Transit Custom", year=2021, license_plate="8T5 7890", daily_price=1690, hourly_price=190,
         category="Van", transmission="Manual", fuel_type="Diesel", seats=9,
         description="Dodávka pro 9 osob nebo stěhování.", branch=2),
    dict(brand="Toyota", model="Yaris", year=2022, license_plate="8T6 2468", daily_price=850, hourly_price=95,
         category="Hatchback", transmission="Automatic", fuel_type="Hybrid", seats=5,
         description="Malý hybrid s automatem.", branch=1),
]


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(User)) == 0:
        for data, role in ((DEMO_ADMIN, UserRole.ADMIN), (DEMO_CUSTOMER, UserRole.CUSTOMER)):
            db.add(User(name=data["name"], email=data["email"],
                        password_hash=hash_password(data["password"]), role=role))
        logger.info("Seeded demo users")

    if db.scalar(select(func.count()).select_from(Branch)) == 0:
        branches = [Branch(**b) for b in BRANCHES]
        db.add_all(branches)
        db.flush()
        if db.scalar(select(func.count()).select_from(Car)) == 0:
            for car in CARS:
                data = dict(car)
                branch = branches[data.pop("branch")]
                db.add(Car(**data, image_url="", branch=branch))
        logger.info("Seeded demo branches and cars")

    db.commit()
