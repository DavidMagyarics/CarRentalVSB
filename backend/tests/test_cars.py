from tests.helpers import auth_headers, create_car, make_admin, register


def test_create_and_list_cars(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    assert car["brand"] == "Škoda"
    assert car["category"] == "SEDAN"

    response = client.get("/cars/")
    assert response.status_code == 200
    cars = response.json()
    assert len(cars) == 1
    assert cars[0]["license_plate"] == "9ZZ0001"


def test_get_car_not_found(client):
    response = client.get("/cars/999")
    assert response.status_code == 404


def test_create_car_requires_login(client):
    response = client.post(
        "/cars/",
        json={
            "brand": "X",
            "model": "Y",
            "year": 2020,
            "license_plate": "Z1",
            "daily_price": 100,
            "hourly_price": 10,
        },
    )
    assert response.status_code == 401


def test_create_car_forbidden_for_customer(client):
    user = register(client)
    response = client.post(
        "/cars/",
        json={
            "brand": "X",
            "model": "Y",
            "year": 2020,
            "license_plate": "Z2",
            "daily_price": 100,
            "hourly_price": 10,
        },
        headers=auth_headers(user["access_token"]),
    )
    assert response.status_code == 403


def test_update_car(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"], license_plate="9ZZ0002")

    response = client.put(
        f"/cars/{car['id']}",
        json={"daily_price": 1500},
        headers=auth_headers(admin["access_token"]),
    )

    assert response.status_code == 200
    assert response.json()["daily_price"] == 1500
    assert response.json()["brand"] == "Škoda"


def test_delete_car(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"], license_plate="9ZZ0003")

    response = client.delete(
        f"/cars/{car['id']}", headers=auth_headers(admin["access_token"])
    )

    assert response.status_code == 204
    assert client.get(f"/cars/{car['id']}").status_code == 404


def test_filter_cars_by_category(client):
    admin = make_admin(client)
    create_car(client, admin["access_token"], license_plate="9ZZ0004", category="SUV")
    create_car(client, admin["access_token"], license_plate="9ZZ0005", category="SEDAN")

    response = client.get("/cars/", params={"category": "SUV"})

    assert response.status_code == 200
    cars = response.json()
    assert len(cars) == 1
    assert cars[0]["category"] == "SUV"


def test_filter_cars_by_price_range(client):
    admin = make_admin(client)
    create_car(
        client, admin["access_token"], license_plate="9ZZ0006", daily_price=500
    )
    create_car(
        client, admin["access_token"], license_plate="9ZZ0007", daily_price=5000
    )

    response = client.get("/cars/", params={"min_price": 1000, "max_price": 6000})

    assert response.status_code == 200
    cars = response.json()
    assert len(cars) == 1
    assert cars[0]["daily_price"] == 5000
