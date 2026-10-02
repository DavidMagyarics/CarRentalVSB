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


def create_branch(client, admin_token, name="Testovací pobočka", address="Testovací 1, Ostrava"):
    response = client.post(
        "/branches/",
        json={"name": name, "address": address},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201
    return response.json()


def create_car(client, admin_token, license_plate="9ZZ0001", **overrides):
    if "branch_id" not in overrides:
        overrides["branch_id"] = create_branch(
            client, admin_token, name=f"Pobočka pro {license_plate}"
        )["id"]
    payload = {
        "brand": "Škoda",
        "model": "Superb",
        "year": 2024,
        "license_plate": license_plate,
        "daily_price": 1200,
        "hourly_price": 100,
        "category": "SEDAN",
        "transmission": "AUTOMATIC",
        "fuel_type": "PETROL",
        "seats": 5,
    }
    payload.update(overrides)
    response = client.post("/cars/", json=payload, headers=auth_headers(admin_token))
    assert response.status_code == 201
    return response.json()
