from dotenv import load_dotenv

load_dotenv()

import logging  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

from datetime import UTC, datetime, timedelta  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from . import crud, models  # noqa: E402
from .database import SessionLocal, engine  # noqa: E402
from .routers import auth, branches, cars, reservations, users  # noqa: E402

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
app.include_router(branches.router)
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

        demo_branches = [
            models.Branch(name="Ostrava – centrum", address="28. října 15, Ostrava"),
            models.Branch(name="Praha – Václavské náměstí", address="Václavské náměstí 1, Praha"),
            models.Branch(name="Brno – hlavní nádraží", address="Nádražní 6, Brno"),
        ]
        db.add_all(demo_branches)
        db.commit()
        for branch in demo_branches:
            db.refresh(branch)

        demo_cars = [
            models.Car(
                brand="Škoda",
                model="Octavia",
                year=2022,
                license_plate="1AB2345",
                daily_price=890,
                hourly_price=80,
                category=models.CarCategory.SEDAN,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.PETROL,
                seats=5,
                description="Prostorný rodinný sedan s nízkou spotřebou a velkým kufrem.",
                image_url="/cars/skoda-octavia.jpg",
                branch_id=demo_branches[0].id,
            ),
            models.Car(
                brand="Škoda",
                model="Fabia",
                year=2021,
                license_plate="2CD6789",
                daily_price=650,
                hourly_price=50,
                category=models.CarCategory.HATCHBACK,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.PETROL,
                seats=5,
                description="Nejlevnější volba do města, snadné parkování.",
                image_url="/cars/skoda-fabia.jpg",
                branch_id=demo_branches[1].id,
            ),
            models.Car(
                brand="Volkswagen",
                model="Golf",
                year=2023,
                license_plate="3EF1122",
                daily_price=990,
                hourly_price=80,
                category=models.CarCategory.HATCHBACK,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.DIESEL,
                seats=5,
                description="Vyvážený hatchback pro město i dálnici.",
                image_url="/cars/volkswagen-golf.jpg",
                branch_id=demo_branches[2].id,
            ),
            models.Car(
                brand="Škoda",
                model="Kodiaq",
                year=2023,
                license_plate="4GH3344",
                daily_price=1450,
                hourly_price=120,
                category=models.CarCategory.SUV,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.DIESEL,
                seats=7,
                description="Prostorné SUV až pro 7 osob, ideální na rodinnou dovolenou.",
                image_url="/cars/skoda-kodiaq.jpg",
                branch_id=demo_branches[0].id,
            ),
            models.Car(
                brand="Tesla",
                model="Model 3",
                year=2024,
                license_plate="5IJ5566",
                daily_price=1990,
                hourly_price=170,
                category=models.CarCategory.SEDAN,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.ELECTRIC,
                seats=5,
                description="Plně elektrický sedan s autopilotem a nulovými emisemi.",
                image_url="/cars/tesla-model-3.jpg",
                branch_id=demo_branches[1].id,
            ),
            models.Car(
                brand="Ford",
                model="Transit",
                year=2020,
                license_plate="6KL7788",
                daily_price=1690,
                hourly_price=140,
                category=models.CarCategory.VAN,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.DIESEL,
                seats=9,
                description="Devítimístný van na stěhování i firemní výlety.",
                image_url="/cars/ford-transit.jpg",
                branch_id=demo_branches[2].id,
            ),
            models.Car(
                brand="Porsche",
                model="911",
                year=2023,
                license_plate="7MN9900",
                daily_price=4990,
                hourly_price=420,
                category=models.CarCategory.SPORTS,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.PETROL,
                seats=2,
                description="Sportovní ikona pro zvláštní příležitosti.",
                image_url="/cars/porsche-911.jpg",
                branch_id=demo_branches[0].id,
            ),
            models.Car(
                brand="Toyota",
                model="Corolla",
                year=2023,
                license_plate="8OP1122",
                daily_price=990,
                hourly_price=80,
                category=models.CarCategory.SEDAN,
                transmission=models.Transmission.AUTOMATIC,
                fuel_type=models.FuelType.HYBRID,
                seats=5,
                description="Spolehlivý hybrid s minimální spotřebou paliva.",
                image_url="/cars/toyota-corolla.jpg",
                branch_id=demo_branches[1].id,
            ),
            models.Car(
                brand="Jeep",
                model="Wrangler",
                year=2022,
                license_plate="9QR3344",
                daily_price=1590,
                hourly_price=130,
                category=models.CarCategory.SUV,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.PETROL,
                seats=5,
                description="Terénní SUV pro výlety mimo silnice.",
                image_url="/cars/jeep-wrangler.jpg",
                branch_id=demo_branches[2].id,
            ),
            models.Car(
                brand="Mini",
                model="Cooper",
                year=2021,
                license_plate="1ST5566",
                daily_price=890,
                hourly_price=70,
                category=models.CarCategory.HATCHBACK,
                transmission=models.Transmission.MANUAL,
                fuel_type=models.FuelType.PETROL,
                seats=4,
                description="Stylový maloauto s výrazným charakterem.",
                image_url="/cars/mini-cooper.jpg",
                branch_id=demo_branches[0].id,
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
        reservation_1_start = now + timedelta(days=3)
        reservation_1_end = now + timedelta(days=6)
        reservation_2_start = now + timedelta(days=20)
        reservation_2_end = now + timedelta(days=24)
        db.add_all(
            [
                models.Reservation(
                    car_id=demo_cars[0].id,
                    user_id=customer.id,
                    status=models.ReservationStatus.CONFIRMED,
                    start_date=reservation_1_start,
                    end_date=reservation_1_end,
                    total_price=crud.calculate_price(
                        demo_cars[0], reservation_1_start, reservation_1_end
                    ),
                    payment_method=models.PaymentMethod.CARD,
                ),
                models.Reservation(
                    car_id=demo_cars[4].id,
                    user_id=customer.id,
                    status=models.ReservationStatus.DRAFT,
                    start_date=reservation_2_start,
                    end_date=reservation_2_end,
                    total_price=crud.calculate_price(
                        demo_cars[4], reservation_2_start, reservation_2_end
                    ),
                    payment_method=models.PaymentMethod.CASH,
                ),
            ]
        )
        db.commit()
        _ = admin
    finally:
        db.close()


_seed_demo_data()
