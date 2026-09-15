def create_car(client, license_plate="9ZZ0001"):
    response = client.post(
        "/cars/",
        json={
            "brand": "Škoda",
            "model": "Superb",
            "year": 2024,
            "license_plate": license_plate,
            "daily_price": 1200,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_and_list_cars(client):
    car = create_car(client)
    assert car["brand"] == "Škoda"

    response = client.get("/cars/")
    assert response.status_code == 200
    cars = response.json()
    assert len(cars) == 1
    assert cars[0]["license_plate"] == "9ZZ0001"


def test_get_car_not_found(client):
    response = client.get("/cars/999")
    assert response.status_code == 404
