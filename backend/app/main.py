from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import SessionLocal, engine
from .routers import cars, reservations, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CarRentalVSB API",
    description="Rezervační systém půjčovny aut – seminární práce z předmětu Softwarové inženýrství (VŠB).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars.router)
app.include_router(reservations.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "CarRentalVSB API"}


def _seed_demo_cars() -> None:
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
            ),
            models.Car(
                brand="Škoda",
                model="Fabia",
                year=2021,
                license_plate="2CD6789",
                daily_price=650,
            ),
            models.Car(
                brand="Volkswagen",
                model="Golf",
                year=2023,
                license_plate="3EF1122",
                daily_price=990,
            ),
        ]
        db.add_all(demo_cars)
        db.commit()
    finally:
        db.close()


_seed_demo_cars()
