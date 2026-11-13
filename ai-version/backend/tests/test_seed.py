"""Demo data on first start."""

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_demo_data_is_seeded_and_demo_accounts_work():
    app = create_app(Settings(database_url="sqlite://", seed_demo_data=True))
    with TestClient(app) as client:
        assert len(client.get("/cars/").json()) >= 3
        assert len(client.get("/branches/").json()) >= 2
        admin = client.post("/auth/login", json={"email": "admin@carrental.cz", "password": "admin123"})
        assert admin.status_code == 200 and admin.json()["user"]["role"] == "ADMIN"
        customer = client.post("/auth/login",
                               json={"email": "customer@carrental.cz", "password": "customer123"})
        assert customer.status_code == 200 and customer.json()["user"]["role"] == "CUSTOMER"
