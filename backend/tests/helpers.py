from app import crud, models


def register(client, name="Jan Novák", email="jan.novak@example.com", password="heslo123"):
    response = client.post(
        "/auth/register", json={"name": name, "email": email, "password": password}
    )
    assert response.status_code == 201
    return response.json()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def make_admin(client, name="Admin", email="admin@example.com", password="admin123"):
    db = client.session_factory()
    try:
        crud.create_user(db, name, email, password, role=models.UserRole.ADMIN)
    finally:
        db.close()
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def create_car(client, admin_token, license_plate="9ZZ0001", **overrides):
    payload = {
        "brand": "Škoda",
        "model": "Superb",
        "year": 2024,
        "license_plate": license_plate,
        "daily_price": 1200,
        "category": "SEDAN",
        "transmission": "AUTOMATIC",
        "fuel_type": "PETROL",
        "seats": 5,
    }
    payload.update(overrides)
    response = client.post("/cars/", json=payload, headers=auth_headers(admin_token))
    assert response.status_code == 201
    return response.json()
