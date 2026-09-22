from tests.helpers import auth_headers, create_car, make_admin, register


def make_reservation_payload(car_id, start="2026-01-10T00:00:00", end="2026-01-15T00:00:00"):
    return {"car_id": car_id, "start_date": start, "end_date": end}


def _customer(client, email="jan.novak@example.com"):
    user = register(client, email=email)
    return user["access_token"], user["user"]


def test_create_reservation_starts_as_draft(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, user = _customer(client)

    response = client.post(
        "/reservations/",
        json=make_reservation_payload(car["id"]),
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    reservation = response.json()
    assert reservation["car_id"] == car["id"]
    assert reservation["status"] == "DRAFT"
    assert reservation["user_id"] == user["id"]
    assert reservation["car"]["brand"] == "Škoda"
    assert reservation["user"]["email"] == "jan.novak@example.com"


def test_create_reservation_requires_login(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])

    response = client.post("/reservations/", json=make_reservation_payload(car["id"]))

    assert response.status_code == 401


def test_reservation_for_unknown_car_returns_404(client):
    token, _ = _customer(client)

    response = client.post(
        "/reservations/", json=make_reservation_payload(999), headers=auth_headers(token)
    )

    assert response.status_code == 404


def test_confirm_reservation(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"]), headers=auth_headers(token)
    ).json()

    response = client.post(
        f"/reservations/{reservation['id']}/confirm", headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"


def test_confirming_unknown_reservation_returns_404(client):
    token, _ = _customer(client)

    response = client.post("/reservations/999/confirm", headers=auth_headers(token))

    assert response.status_code == 404


def test_cannot_confirm_someone_elses_reservation(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    owner_token, _ = _customer(client)
    reservation = client.post(
        "/reservations/",
        json=make_reservation_payload(car["id"]),
        headers=auth_headers(owner_token),
    ).json()
    other_token, _ = _customer(client, email="other@example.com")

    response = client.post(
        f"/reservations/{reservation['id']}/confirm", headers=auth_headers(other_token)
    )

    assert response.status_code == 403


def test_admin_can_confirm_any_reservation(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    owner_token, _ = _customer(client)
    reservation = client.post(
        "/reservations/",
        json=make_reservation_payload(car["id"]),
        headers=auth_headers(owner_token),
    ).json()

    response = client.post(
        f"/reservations/{reservation['id']}/confirm",
        headers=auth_headers(admin["access_token"]),
    )

    assert response.status_code == 200


def test_confirming_already_confirmed_reservation_fails(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"]), headers=auth_headers(token)
    ).json()
    client.post(f"/reservations/{reservation['id']}/confirm", headers=auth_headers(token))

    response = client.post(
        f"/reservations/{reservation['id']}/confirm", headers=auth_headers(token)
    )

    assert response.status_code == 409


def test_two_drafts_for_same_slot_can_coexist_but_only_one_can_be_confirmed(client):
    """Common business rule: two CONFIRMED reservations of the same resource
    must not overlap. DRAFTs may coexist since they are not yet binding."""
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token_a, _ = _customer(client, email="a@example.com")
    token_b, _ = _customer(client, email="b@example.com")
    payload = make_reservation_payload(
        car["id"], start="2026-02-01T00:00:00", end="2026-02-10T00:00:00"
    )

    first = client.post("/reservations/", json=payload, headers=auth_headers(token_a)).json()
    second = client.post("/reservations/", json=payload, headers=auth_headers(token_b)).json()
    assert first["status"] == "DRAFT"
    assert second["status"] == "DRAFT"

    assert (
        client.post(f"/reservations/{first['id']}/confirm", headers=auth_headers(token_a)).status_code
        == 200
    )
    response = client.post(
        f"/reservations/{second['id']}/confirm", headers=auth_headers(token_b)
    )

    assert response.status_code == 409


def test_create_rejects_slot_already_confirmed(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    first = make_reservation_payload(
        car["id"], start="2026-03-01T00:00:00", end="2026-03-10T00:00:00"
    )
    overlapping = make_reservation_payload(
        car["id"], start="2026-03-05T00:00:00", end="2026-03-12T00:00:00"
    )

    reservation = client.post(
        "/reservations/", json=first, headers=auth_headers(token)
    ).json()
    client.post(f"/reservations/{reservation['id']}/confirm", headers=auth_headers(token))

    response = client.post(
        "/reservations/", json=overlapping, headers=auth_headers(token)
    )

    assert response.status_code == 409


def test_non_overlapping_confirmed_reservations_are_accepted(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    first = make_reservation_payload(
        car["id"], start="2026-04-01T00:00:00", end="2026-04-05T00:00:00"
    )
    second = make_reservation_payload(
        car["id"], start="2026-04-05T00:00:00", end="2026-04-10T00:00:00"
    )

    r1 = client.post("/reservations/", json=first, headers=auth_headers(token)).json()
    r2 = client.post("/reservations/", json=second, headers=auth_headers(token)).json()

    assert (
        client.post(f"/reservations/{r1['id']}/confirm", headers=auth_headers(token)).status_code
        == 200
    )
    assert (
        client.post(f"/reservations/{r2['id']}/confirm", headers=auth_headers(token)).status_code
        == 200
    )


def test_end_date_must_be_after_start_date(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    payload = make_reservation_payload(
        car["id"], start="2026-04-10T00:00:00", end="2026-04-01T00:00:00"
    )

    response = client.post("/reservations/", json=payload, headers=auth_headers(token))

    assert response.status_code == 422


def test_cancel_draft_reservation(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"]), headers=auth_headers(token)
    ).json()

    response = client.post(
        f"/reservations/{reservation['id']}/cancel", headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancel_confirmed_reservation_before_start_date(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    payload = make_reservation_payload(
        car["id"], start="2099-01-10T00:00:00", end="2099-01-15T00:00:00"
    )
    reservation = client.post(
        "/reservations/", json=payload, headers=auth_headers(token)
    ).json()
    client.post(f"/reservations/{reservation['id']}/confirm", headers=auth_headers(token))

    response = client.post(
        f"/reservations/{reservation['id']}/cancel", headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cannot_cancel_confirmed_reservation_after_start_date(client):
    """Domain-specific business rule: once the rental period has begun, a
    confirmed reservation can no longer be cancelled through the system."""
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    payload = make_reservation_payload(
        car["id"], start="2020-01-10T00:00:00", end="2020-01-15T00:00:00"
    )
    reservation = client.post(
        "/reservations/", json=payload, headers=auth_headers(token)
    ).json()
    client.post(f"/reservations/{reservation['id']}/confirm", headers=auth_headers(token))

    response = client.post(
        f"/reservations/{reservation['id']}/cancel", headers=auth_headers(token)
    )

    assert response.status_code == 409


def test_cancelling_already_cancelled_reservation_fails(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    reservation = client.post(
        "/reservations/", json=make_reservation_payload(car["id"]), headers=auth_headers(token)
    ).json()
    client.post(f"/reservations/{reservation['id']}/cancel", headers=auth_headers(token))

    response = client.post(
        f"/reservations/{reservation['id']}/cancel", headers=auth_headers(token)
    )

    assert response.status_code == 409


def test_availability_reflects_confirmed_reservations_only(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    payload = make_reservation_payload(
        car["id"], start="2026-06-01T00:00:00", end="2026-06-10T00:00:00"
    )
    reservation = client.post(
        "/reservations/", json=payload, headers=auth_headers(token)
    ).json()

    still_available = client.get(
        f"/cars/{car['id']}/availability",
        params={"start_date": "2026-06-05T00:00:00", "end_date": "2026-06-08T00:00:00"},
    ).json()
    assert still_available["available"] is True

    client.post(f"/reservations/{reservation['id']}/confirm", headers=auth_headers(token))

    now_unavailable = client.get(
        f"/cars/{car['id']}/availability",
        params={"start_date": "2026-06-05T00:00:00", "end_date": "2026-06-08T00:00:00"},
    ).json()
    assert now_unavailable["available"] is False


def test_list_my_reservations_only_returns_own(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token_a, _ = _customer(client, email="a@example.com")
    token_b, _ = _customer(client, email="b@example.com")
    client.post(
        "/reservations/",
        json=make_reservation_payload(car["id"], start="2026-07-01T00:00:00", end="2026-07-05T00:00:00"),
        headers=auth_headers(token_a),
    )
    client.post(
        "/reservations/",
        json=make_reservation_payload(car["id"], start="2026-08-01T00:00:00", end="2026-08-05T00:00:00"),
        headers=auth_headers(token_b),
    )

    response = client.get("/reservations/me", headers=auth_headers(token_a))

    assert response.status_code == 200
    reservations = response.json()
    assert len(reservations) == 1
    assert reservations[0]["user"]["email"] == "a@example.com"


def test_list_all_reservations_requires_admin(client):
    token, _ = _customer(client)

    response = client.get("/reservations/", headers=auth_headers(token))

    assert response.status_code == 403


def test_admin_sees_all_reservations(client):
    admin = make_admin(client)
    car = create_car(client, admin["access_token"])
    token, _ = _customer(client)
    client.post(
        "/reservations/", json=make_reservation_payload(car["id"]), headers=auth_headers(token)
    )

    response = client.get("/reservations/", headers=auth_headers(admin["access_token"]))

    assert response.status_code == 200
    assert len(response.json()) == 1
