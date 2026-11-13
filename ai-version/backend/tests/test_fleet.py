"""UC3 Browse & filter cars, UC9 Manage fleet."""

from app.models import Reservation

from .conftest import reservation_body

NEW_CAR = {
    "brand": "Ford", "model": "Focus", "year": 2021, "license_plate": "9X9 9999",
    "daily_price": 900, "hourly_price": 110, "category": "Hatchback",
    "transmission": "Manual", "fuel_type": "Petrol", "seats": 5,
    "description": "", "image_url": "",
}


def test_list_all_cars_without_filters(client, cars):
    response = client.get("/cars/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert {"daily_price", "hourly_price", "branch", "image_url"} <= data[0].keys()
    assert data[0]["branch"]["name"] == "Ostrava"


def test_filter_by_category_transmission_fuel(client, cars):
    assert [c["model"] for c in client.get("/cars/?category=SUV").json()] == ["Tucson"]
    assert len(client.get("/cars/?transmission=Automatic").json()) == 2
    assert [c["model"] for c in client.get("/cars/?fuel_type=electric").json()] == ["Model 3"]


def test_filter_by_price_range_and_branch(client, cars, branches):
    models = [c["model"] for c in client.get("/cars/?min_price=1000&max_price=1600").json()]
    assert models == ["Tucson"]
    by_branch = client.get(f"/cars/?branch_id={branches[1].id}").json()
    assert [c["model"] for c in by_branch] == ["Model 3"]


def test_no_car_matches_returns_empty_list(client, cars):
    response = client.get("/cars/?category=Truck")
    assert response.status_code == 200
    assert response.json() == []


def test_list_branches(client, branches):
    assert [b["name"] for b in client.get("/branches/").json()] == ["Ostrava", "Praha"]


def test_admin_creates_car(client, admin_headers, branches):
    response = client.post("/cars/", json={**NEW_CAR, "branch_id": branches[0].id},
                           headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["license_plate"] == "9X9 9999"
    assert len(client.get("/cars/").json()) == 1


def test_create_car_with_unknown_category_transmission_or_fuel_is_422(client, admin_headers,
                                                                     branches):
    for field, value in (("category", "blabla"), ("transmission", "xyz"), ("fuel_type", "water")):
        body = {**NEW_CAR, "branch_id": branches[0].id, field: value}
        assert client.post("/cars/", json=body, headers=admin_headers).status_code == 422
    assert client.get("/cars/").json() == []


def test_update_car_with_unknown_category_is_422(client, admin_headers, car):
    response = client.put(f"/cars/{car.id}", json={"category": "blabla"}, headers=admin_headers)
    assert response.status_code == 422


def test_hourly_price_above_daily_price_is_422(client, admin_headers, branches, car):
    body = {**NEW_CAR, "branch_id": branches[0].id, "daily_price": 100, "hourly_price": 5000}
    response = client.post("/cars/", json=body, headers=admin_headers)
    assert response.status_code == 422
    assert response.json()["detail"] == "Cena za hodinu nesmí být vyšší než cena za den"
    # editing only one of the prices is checked against the other stored one
    too_cheap_day = client.put(f"/cars/{car.id}", json={"daily_price": 50}, headers=admin_headers)
    assert too_cheap_day.status_code == 422
    same = client.put(f"/cars/{car.id}", json={"hourly_price": car.daily_price}, headers=admin_headers)
    assert same.status_code == 200


def test_create_car_with_unknown_branch_is_404(client, admin_headers, branches):
    response = client.post("/cars/", json={**NEW_CAR, "branch_id": 999}, headers=admin_headers)
    assert response.status_code == 404


def test_customer_cannot_manage_fleet(client, customer_headers, car, branches):
    create = client.post("/cars/", json={**NEW_CAR, "branch_id": branches[0].id},
                         headers=customer_headers)
    update = client.put(f"/cars/{car.id}", json={"daily_price": 1}, headers=customer_headers)
    delete = client.delete(f"/cars/{car.id}", headers=customer_headers)
    for response in (create, update, delete):
        assert response.status_code == 403
        assert response.json()["detail"] == "Vyžadována jsou práva administrátora"


def test_fleet_management_requires_login(client, car):
    assert client.delete(f"/cars/{car.id}").status_code == 401


def test_admin_updates_car(client, admin_headers, car, branches):
    response = client.put(f"/cars/{car.id}", json={"daily_price": 999, "branch_id": branches[1].id},
                          headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["daily_price"] == 999
    assert response.json()["branch"]["name"] == "Praha"
    assert response.json()["model"] == "Fabia"  # untouched fields stay


def test_update_unknown_car_is_404(client, admin_headers, cars):
    assert client.put("/cars/999", json={"daily_price": 1}, headers=admin_headers).status_code == 404


def test_duplicate_license_plate_is_409(client, admin_headers, car, branches):
    response = client.post("/cars/", json={**NEW_CAR, "license_plate": car.license_plate,
                                           "branch_id": branches[0].id}, headers=admin_headers)
    assert response.status_code == 409


def test_delete_car_deletes_its_reservations(client, admin_headers, customer_headers, car, db):
    created = client.post("/reservations/", json=reservation_body(car.id), headers=customer_headers)
    assert created.status_code == 201

    response = client.delete(f"/cars/{car.id}", headers=admin_headers)
    assert response.status_code == 204
    assert client.get(f"/cars/{car.id}").status_code == 404
    db.expire_all()
    assert db.query(Reservation).count() == 0
    assert client.get("/reservations/me", headers=customer_headers).json() == []


# --- Car categories (version 2.0) ----------------------------------------------
def test_default_categories_exist(client):
    names = [c["name"] for c in client.get("/categories/").json()]
    assert names == ["Combi", "Hatchback", "SUV", "Sedan", "Van"]


def test_admin_adds_category_and_uses_it_for_a_car(client, admin_headers, branches):
    created = client.post("/categories/", json={"name": "Kabriolet"}, headers=admin_headers)
    assert created.status_code == 201
    body = {**NEW_CAR, "branch_id": branches[0].id, "category": "kabriolet"}
    car = client.post("/cars/", json=body, headers=admin_headers)
    assert car.status_code == 201
    assert car.json()["category"] == "Kabriolet"  # stored with the category's spelling


def test_duplicate_category_is_409(client, admin_headers):
    response = client.post("/categories/", json={"name": "suv"}, headers=admin_headers)
    assert response.status_code == 409


def test_category_used_by_a_car_cannot_be_deleted(client, admin_headers, car):
    category = next(c for c in client.get("/categories/").json() if c["name"] == car.category)
    response = client.delete(f"/categories/{category['id']}", headers=admin_headers)
    assert response.status_code == 409


def test_admin_deletes_unused_category(client, admin_headers):
    category = next(c for c in client.get("/categories/").json() if c["name"] == "Van")
    assert client.delete(f"/categories/{category['id']}", headers=admin_headers).status_code == 204
    assert "Van" not in [c["name"] for c in client.get("/categories/").json()]
    assert client.delete(f"/categories/{category['id']}", headers=admin_headers).status_code == 404


def test_customer_cannot_manage_categories(client, customer_headers):
    assert client.post("/categories/", json={"name": "X"}, headers=customer_headers).status_code == 403
    assert client.delete("/categories/1", headers=customer_headers).status_code == 403
