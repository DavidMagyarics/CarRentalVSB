from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models
from .database import SessionLocal, engine
from .routers import auth, cars, reservations, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CarRentalVSB API",
    description="Rezervační systém půjčovny aut – seminární práce z předmětu Softwarové inženýrství (VŠB).",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(reservations.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "CarRentalVSB API"}


def _seed_demo_data() -> None:
    db = SessionLocal()
    try:
        if db.query(models.Car).count() > 0:
            return

        demo_cars = [
            models.Car(
                brand="Škoda",
                model="Octavia",
                year=2022,
                license_plate="1AB2345",
                daily_price=890,
                category=models.CarCategory.SEDAN,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.PETROL,
                seats=5,
                description="Prostorný rodinný sedan s nízkou spotřebou a velkým kufrem.",
            ),
            models.Car(
                brand="Škoda",
                model="Fabia",
                year=2021,
                license_plate="2CD6789",
                daily_price=650,
                category=models.CarCategory.HATCHBACK,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.PETROL,
                seats=5,
                description="Nejlevnější volba do města, snadné parkování.",
            ),
            models.Car(
                brand="Volkswagen",
                model="Golf",
                year=2023,
                license_plate="3EF1122",
                daily_price=990,
                category=models.CarCategory.HATCHBACK,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.DIESEL,
                seats=5,
                description="Vyvážený hatchback pro město i dálnici.",
            ),
            models.Car(
                brand="Škoda",
                model="Kodiaq",
                year=2023,
                license_plate="4GH3344",
                daily_price=1450,
                category=models.CarCategory.SUV,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.DIESEL,
                seats=7,
                description="Prostorné SUV až pro 7 osob, ideální na rodinnou dovolenou.",
            ),
            models.Car(
                brand="Tesla",
                model="Model 3",
                year=2024,
                license_plate="5IJ5566",
                daily_price=1990,
                category=models.CarCategory.SEDAN,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.ELECTRIC,
                seats=5,
                description="Plně elektrický sedan s autopilotem a nulovými emisemi.",
            ),
            models.Car(
                brand="Ford",
                model="Transit",
                year=2020,
                license_plate="6KL7788",
                daily_price=1690,
                category=models.CarCategory.VAN,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.DIESEL,
                seats=9,
                description="Devítimístný van na stěhování i firemní výlety.",
            ),
            models.Car(
                brand="Porsche",
                model="911",
                year=2023,
                license_plate="7MN9900",
                daily_price=4990,
                category=models.CarCategory.SPORTS,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.PETROL,
                seats=2,
                description="Sportovní ikona pro zvláštní příležitosti.",
            ),
            models.Car(
                brand="Toyota",
                model="Corolla",
                year=2023,
                license_plate="8OP1122",
                daily_price=990,
                category=models.CarCategory.SEDAN,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.HYBRID,
                seats=5,
                description="Spolehlivý hybrid s minimální spotřebou paliva.",
            ),
            models.Car(
                brand="Jeep",
                model="Wrangler",
                year=2022,
                license_plate="9QR3344",
                daily_price=1590,
                category=models.CarCategory.SUV,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.PETROL,
                seats=5,
                description="Terénní SUV pro výlety mimo silnice.",
            ),
            models.Car(
                brand="Mini",
                model="Cooper",
                year=2021,
                license_plate="1ST5566",
                daily_price=890,
                category=models.CarCategory.HATCHBACK,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.PETROL,
                seats=4,
                description="Stylový maloauto s výrazným charakterem.",
            ),
        ]
        db.add_all(demo_cars)
        db.commit()

        admin = crud.create_user(
            db, "Admin", "admin@carrentalvsb.cz", "admin123", role=models.UserRole.ADMIN
        )
        customer = crud.create_user(
            db, "Jan Novák", "jan.novak@example.com", "heslo123"
        )

        now = datetime.now(UTC)
        db.add_all(
            [
                models.Reservation(
                    car_id=demo_cars[0].id,
                    user_id=customer.id,
                    status=models.ReservationStatus.CONFIRMED,
                    start_date=now + timedelta(days=3),
                    end_date=now + timedelta(days=6),
                ),
                models.Reservation(
                    car_id=demo_cars[4].id,
                    user_id=customer.id,
                    status=models.ReservationStatus.DRAFT,
                    start_date=now + timedelta(days=20),
                    end_date=now + timedelta(days=24),
                ),
            ]
        )
        db.commit()
        _ = admin
    finally:
        db.close()


_seed_demo_data()
