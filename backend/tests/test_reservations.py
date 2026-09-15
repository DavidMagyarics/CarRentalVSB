from tests.test_cars import create_car


def make_reservation_payload(car_id, start="2026-01-10T00:00:00", end="2026-01-15T00:00:00"):
    return {
        "car_id": car_id,
        "customer_name": "Jan Novák",
        "customer_email": "jan.novak@example.com",
        "start_date": start,
        "end_date": end,
    }


def test_create_reservation_starts_as_draft(client):
    car = create_car(client)

    response = client.post(
        "/reservations/", json=make_reservation_payload(car["id"])
    )

    assert response.status_code == 201
    reservation = response.json()
    assert reservation["car_id"] == car["id"]
    assert reservation["status"] == "DRAFT"
    assert reservation["user_id"] is not None


def test_reservation_creates_user(client):
    car = create_car(client)
    client.post("/reservations/", json=make_reservation_payload(car["id"]))

    users = client.get("/users/").json()

    assert len(users) == 1
    assert users[0]["email"] == "jan.novak@example.com"
    assert users[0]["name"] == "Jan Novák"


def test_reservation_for_unknown_car_returns_404(client):
    response = client.post("/reservations/", json=make_reservation_payload(999))
    assert response.status_code == 404


def test_confirm_reservation(client):
    car = create_car(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"])
    ).json()

    response = client.post(f"/reservations/{reservation['id']}/confirm")

    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"


def test_confirming_unknown_reservation_returns_404(client):
    response = client.post("/reservations/999/confirm")
    assert response.status_code == 404


def test_confirming_already_confirmed_reservation_fails(client):
    car = create_car(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"])
    ).json()
    client.post(f"/reservations/{reservation['id']}/confirm")

    response = client.post(f"/reservations/{reservation['id']}/confirm")

    assert response.status_code == 409


def test_two_drafts_for_same_slot_can_coexist_but_only_one_can_be_confirmed(client):
    """Common business rule: two CONFIRMED reservations of the same resource
    must not overlap. DRAFTs may coexist since they are not yet binding."""
    car = create_car(client)
    payload = make_reservation_payload(
        car["id"], start="2026-02-01T00:00:00", end="2026-02-10T00:00:00"
    )

    first = client.post("/reservations/", json=payload).json()
    second = client.post("/reservations/", json=payload).json()
    assert first["status"] == "DRAFT"
    assert second["status"] == "DRAFT"

    assert client.post(f"/reservations/{first['id']}/confirm").status_code == 200
    response = client.post(f"/reservations/{second['id']}/confirm")

    assert response.status_code == 409


def test_create_rejects_slot_already_confirmed(client):
    car = create_car(client)
    first = make_reservation_payload(
        car["id"], start="2026-03-01T00:00:00", end="2026-03-10T00:00:00"
    )
    overlapping = make_reservation_payload(
        car["id"], start="2026-03-05T00:00:00", end="2026-03-12T00:00:00"
    )

    reservation = client.post("/reservations/", json=first).json()
    client.post(f"/reservations/{reservation['id']}/confirm")

    response = client.post("/reservations/", json=overlapping)

    assert response.status_code == 409


def test_non_overlapping_confirmed_reservations_are_accepted(client):
    car = create_car(client)
    first = make_reservation_payload(
        car["id"], start="2026-04-01T00:00:00", end="2026-04-05T00:00:00"
    )
    second = make_reservation_payload(
        car["id"], start="2026-04-05T00:00:00", end="2026-04-10T00:00:00"
    )

    r1 = client.post("/reservations/", json=first).json()
    r2 = client.post("/reservations/", json=second).json()

    assert client.post(f"/reservations/{r1['id']}/confirm").status_code == 200
    assert client.post(f"/reservations/{r2['id']}/confirm").status_code == 200


def test_end_date_must_be_after_start_date(client):
    car = create_car(client)
    payload = make_reservation_payload(
        car["id"], start="2026-04-10T00:00:00", end="2026-04-01T00:00:00"
    )

    response = client.post("/reservations/", json=payload)

    assert response.status_code == 422


def test_cancel_draft_reservation(client):
    car = create_car(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"])
    ).json()

    response = client.post(f"/reservations/{reservation['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancel_confirmed_reservation_before_start_date(client):
    car = create_car(client)
    payload = make_reservation_payload(
        car["id"], start="2099-01-10T00:00:00", end="2099-01-15T00:00:00"
    )
    reservation = client.post("/reservations/", json=payload).json()
    client.post(f"/reservations/{reservation['id']}/confirm")

    response = client.post(f"/reservations/{reservation['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cannot_cancel_confirmed_reservation_after_start_date(client):
    """Domain-specific business rule: once the rental period has begun, a
    confirmed reservation can no longer be cancelled through the system."""
    car = create_car(client)
    payload = make_reservation_payload(
        car["id"], start="2020-01-10T00:00:00", end="2020-01-15T00:00:00"
    )
    reservation = client.post("/reservations/", json=payload).json()
    client.post(f"/reservations/{reservation['id']}/confirm")

    response = client.post(f"/reservations/{reservation['id']}/cancel")

    assert response.status_code == 409


def test_cancelling_already_cancelled_reservation_fails(client):
    car = create_car(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"])
    ).json()
    client.post(f"/reservations/{reservation['id']}/cancel")

    response = client.post(f"/reservations/{reservation['id']}/cancel")

    assert response.status_code == 409


def test_availability_reflects_confirmed_reservations_only(client):
    car = create_car(client)
    payload = make_reservation_payload(
        car["id"], start="2026-06-01T00:00:00", end="2026-06-10T00:00:00"
    )
    reservation = client.post("/reservations/", json=payload).json()

    still_available = client.get(
        f"/cars/{car['id']}/availability",
        params={"start_date": "2026-06-05T00:00:00", "end_date": "2026-06-08T00:00:00"},
    ).json()
    assert still_available["available"] is True

    client.post(f"/reservations/{reservation['id']}/confirm")

    now_unavailable = client.get(
        f"/cars/{car['id']}/availability",
        params={"start_date": "2026-06-05T00:00:00", "end_date": "2026-06-08T00:00:00"},
    ).json()
    assert now_unavailable["available"] is False
