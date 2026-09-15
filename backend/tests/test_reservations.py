from tests.test_cars import create_car


def make_reservation_payload(car_id, start="2026-01-10T00:00:00", end="2026-01-15T00:00:00"):
    return {
        "car_id": car_id,
        "customer_name": "Jan Novák",
        "customer_email": "jan.novak@example.com",
        "start_date": start,
        "end_date": end,
    }


def test_create_reservation(client):
    car = create_car(client)

    response = client.post(
        "/reservations/", json=make_reservation_payload(car["id"])
    )

    assert response.status_code == 201
    reservation = response.json()
    assert reservation["car_id"] == car["id"]
    assert reservation["customer_name"] == "Jan Novák"


def test_reservation_for_unknown_car_returns_404(client):
    response = client.post("/reservations/", json=make_reservation_payload(999))
    assert response.status_code == 404


def test_overlapping_reservation_is_rejected(client):
    car = create_car(client)
    first = make_reservation_payload(
        car["id"], start="2026-02-01T00:00:00", end="2026-02-10T00:00:00"
    )
    overlapping = make_reservation_payload(
        car["id"], start="2026-02-05T00:00:00", end="2026-02-12T00:00:00"
    )

    assert client.post("/reservations/", json=first).status_code == 201
    response = client.post("/reservations/", json=overlapping)

    assert response.status_code == 409


def test_non_overlapping_reservation_is_accepted(client):
    car = create_car(client)
    first = make_reservation_payload(
        car["id"], start="2026-03-01T00:00:00", end="2026-03-05T00:00:00"
    )
    second = make_reservation_payload(
        car["id"], start="2026-03-05T00:00:00", end="2026-03-10T00:00:00"
    )

    assert client.post("/reservations/", json=first).status_code == 201
    assert client.post("/reservations/", json=second).status_code == 201


def test_end_date_must_be_after_start_date(client):
    car = create_car(client)
    payload = make_reservation_payload(
        car["id"], start="2026-04-10T00:00:00", end="2026-04-01T00:00:00"
    )

    response = client.post("/reservations/", json=payload)

    assert response.status_code == 422
