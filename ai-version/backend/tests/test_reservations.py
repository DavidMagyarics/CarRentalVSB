"""UC4 Create reservation, UC4a Check availability, UC5 Cancel, UC6, UC8, UC10."""

from datetime import datetime

from app.models import Reservation

from .conftest import reservation_body


def _create(client, headers, car_id, **kwargs):
    return client.post("/reservations/", json=reservation_body(car_id, **kwargs), headers=headers)


def _create_and_confirm(client, customer_headers, admin_headers, car_id, **kwargs):
    created = _create(client, customer_headers, car_id, **kwargs)
    assert created.status_code == 201, created.text
    rid = created.json()["id"]
    confirmed = client.post(f"/reservations/{rid}/confirm", headers=admin_headers)
    assert confirmed.status_code == 200, confirmed.text
    return rid


# --- UC4 ---------------------------------------------------------------------
def test_create_reservation_is_draft_with_price(client, customer_headers, car):
    response = _create(client, customer_headers, car.id, payment="CARD")
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "DRAFT"
    assert body["payment_method"] == "CARD"
    # Mon 09:00 -> Wed 10:00 = 2 days + 1 h = 2*800 + 100
    assert body["total_price"] == 1700
    assert body["car"]["model"] == "Fabia"
    assert body["user"]["email"] == "customer@test.cz"


def test_create_reservation_requires_login(client, car):
    assert client.post("/reservations/", json=reservation_body(car.id)).status_code == 401


def test_admin_cannot_create_reservation(client, admin_headers, car, db):
    response = _create(client, admin_headers, car.id)
    assert response.status_code == 403
    assert response.json()["detail"] == "Rezervaci může vytvořit jen zákazník"
    assert db.query(Reservation).count() == 0


def test_create_reservation_unknown_car_is_404(client, customer_headers, cars):
    assert _create(client, customer_headers, 999).status_code == 404


def test_create_reservation_outside_opening_hours_is_422(client, customer_headers, car):
    too_early = _create(client, customer_headers, car.id, start="2030-01-07T07:30")
    too_late = _create(client, customer_headers, car.id, end="2030-01-09T20:30")
    saturday = _create(client, customer_headers, car.id, start="2030-01-12T10:00",
                       end="2030-01-14T10:00")
    for response in (too_early, too_late, saturday):
        assert response.status_code == 422
        assert response.json()["detail"].startswith("Vyzvednutí i vrácení auta jsou možné")


def test_opening_hours_boundaries_are_allowed(client, customer_headers, car):
    response = _create(client, customer_headers, car.id, start="2030-01-07T08:00",
                       end="2030-01-07T20:00")
    assert response.status_code == 201


def test_return_before_pickup_is_422(client, customer_headers, car):
    response = _create(client, customer_headers, car.id, start="2030-01-09T10:00",
                       end="2030-01-08T10:00")
    assert response.status_code == 422


def test_pickup_in_the_past_is_422(client, customer_headers, car):
    response = _create(client, customer_headers, car.id, start="2030-01-02T10:00",
                       end="2030-01-08T10:00")
    assert response.status_code == 422


def test_invalid_payment_method_is_422(client, customer_headers, car):
    assert _create(client, customer_headers, car.id, payment="BITCOIN").status_code == 422


def test_create_over_confirmed_slot_is_409(client, customer_headers, other_headers,
                                           admin_headers, car):
    _create_and_confirm(client, customer_headers, admin_headers, car.id)
    response = _create(client, other_headers, car.id, start="2030-01-08T09:00",
                       end="2030-01-10T09:00")
    assert response.status_code == 409
    assert response.json()["detail"] == "Auto je v požadovaném termínu již potvrzenou rezervací obsazeno"


def test_draft_reservations_do_not_block_the_slot(client, customer_headers, other_headers, car):
    assert _create(client, customer_headers, car.id).status_code == 201
    assert _create(client, other_headers, car.id).status_code == 201


def test_adjacent_reservation_does_not_overlap(client, customer_headers, other_headers,
                                               admin_headers, car):
    _create_and_confirm(client, customer_headers, admin_headers, car.id)  # ends Wed 10:00
    response = _create(client, other_headers, car.id, start="2030-01-09T10:00",
                       end="2030-01-09T12:00")
    assert response.status_code == 201


# --- UC4a --------------------------------------------------------------------
def test_availability_endpoint(client, customer_headers, admin_headers, car, cars):
    url = f"/cars/{car.id}/availability?start_date=2030-01-08T09:00&end_date=2030-01-08T12:00"
    assert client.get(url).json()["available"] is True
    _create_and_confirm(client, customer_headers, admin_headers, car.id)
    assert client.get(url).json()["available"] is False
    other_car = cars[1].id
    other_url = url.replace(f"/cars/{car.id}/", f"/cars/{other_car}/")
    assert client.get(other_url).json()["available"] is True


def test_availability_unknown_car_404_and_bad_range_422(client, car):
    assert client.get("/cars/999/availability?start_date=2030-01-08T09:00"
                      "&end_date=2030-01-08T12:00").status_code == 404
    assert client.get(f"/cars/{car.id}/availability?start_date=2030-01-08T12:00"
                      "&end_date=2030-01-08T09:00").status_code == 422


def test_cancelled_reservation_frees_the_slot(client, customer_headers, admin_headers, car):
    rid = _create_and_confirm(client, customer_headers, admin_headers, car.id)
    url = f"/cars/{car.id}/availability?start_date=2030-01-08T09:00&end_date=2030-01-08T12:00"
    assert client.get(url).json()["available"] is False
    assert client.post(f"/reservations/{rid}/cancel", headers=customer_headers).status_code == 200
    assert client.get(url).json()["available"] is True


# --- UC8 / UC8a --------------------------------------------------------------
def test_admin_confirms_draft_and_notification_is_sent(client, customer_headers, admin_headers,
                                                       car, notifier):
    rid = _create(client, customer_headers, car.id).json()["id"]
    response = client.post(f"/reservations/{rid}/confirm", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"
    assert notifier.sent == [(rid, "customer@test.cz")]


def test_customer_cannot_confirm(client, customer_headers, car):
    rid = _create(client, customer_headers, car.id).json()["id"]
    response = client.post(f"/reservations/{rid}/confirm", headers=customer_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Vyžadována jsou práva administrátora"


def test_confirm_unknown_reservation_is_404(client, admin_headers):
    assert client.post("/reservations/999/confirm", headers=admin_headers).status_code == 404


def test_confirm_non_draft_is_409(client, customer_headers, admin_headers, car, notifier):
    rid = _create_and_confirm(client, customer_headers, admin_headers, car.id)
    again = client.post(f"/reservations/{rid}/confirm", headers=admin_headers)
    assert again.status_code == 409
    assert again.json()["detail"] == "Rezervaci ve stavu CONFIRMED nelze potvrdit"

    client.post(f"/reservations/{rid}/cancel", headers=admin_headers)
    cancelled = client.post(f"/reservations/{rid}/confirm", headers=admin_headers)
    assert cancelled.status_code == 409
    assert cancelled.json()["detail"] == "Rezervaci ve stavu CANCELLED nelze potvrdit"
    assert len(notifier.sent) == 1


def test_confirm_when_slot_taken_in_the_meantime_is_409(client, customer_headers, other_headers,
                                                         admin_headers, car, notifier):
    first = _create(client, customer_headers, car.id).json()["id"]
    second = _create(client, other_headers, car.id, start="2030-01-08T09:00",
                     end="2030-01-10T09:00").json()["id"]
    assert client.post(f"/reservations/{first}/confirm", headers=admin_headers).status_code == 200
    response = client.post(f"/reservations/{second}/confirm", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Auto je v tomto termínu už jinou rezervací potvrzeno"
    assert notifier.sent == [(first, "customer@test.cz")]


def test_failed_notification_keeps_reservation_confirmed(client, customer_headers, admin_headers,
                                                         car, notifier):
    notifier.result = False
    rid = _create(client, customer_headers, car.id).json()["id"]
    response = client.post(f"/reservations/{rid}/confirm", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"


# --- UC5 ---------------------------------------------------------------------
def test_owner_cancels_draft(client, customer_headers, car):
    rid = _create(client, customer_headers, car.id).json()["id"]
    response = client.post(f"/reservations/{rid}/cancel", headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_admin_cancels_any_reservation(client, customer_headers, admin_headers, car):
    rid = _create_and_confirm(client, customer_headers, admin_headers, car.id)
    response = client.post(f"/reservations/{rid}/cancel", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_other_customer_cannot_cancel_is_403(client, customer_headers, other_headers, car):
    rid = _create(client, customer_headers, car.id).json()["id"]
    response = client.post(f"/reservations/{rid}/cancel", headers=other_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Tato rezervace vám nepatří"


def test_cancel_unknown_reservation_is_404(client, customer_headers):
    assert client.post("/reservations/999/cancel", headers=customer_headers).status_code == 404


def test_cancel_twice_is_409(client, customer_headers, car):
    rid = _create(client, customer_headers, car.id).json()["id"]
    client.post(f"/reservations/{rid}/cancel", headers=customer_headers)
    response = client.post(f"/reservations/{rid}/cancel", headers=customer_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Rezervace je již zrušena"


def test_cannot_cancel_confirmed_after_rental_started(client, customer_headers, admin_headers,
                                                       car, clock):
    rid = _create_and_confirm(client, customer_headers, admin_headers, car.id)
    clock.now = datetime(2030, 1, 7, 9, 0)  # == start_date -> "Rental started"
    response = client.post(f"/reservations/{rid}/cancel", headers=customer_headers)
    assert response.status_code == 409
    assert response.json()["detail"].startswith("Potvrzenou rezervaci nelze zrušit")
    mine = client.get("/reservations/me", headers=customer_headers).json()
    assert mine[0]["rental_started"] is True
    assert mine[0]["status"] == "CONFIRMED"


def test_draft_can_be_cancelled_even_after_start(client, customer_headers, car, clock):
    rid = _create(client, customer_headers, car.id).json()["id"]
    clock.now = datetime(2030, 1, 8, 12, 0)
    assert client.post(f"/reservations/{rid}/cancel", headers=customer_headers).status_code == 200


# --- Return the car: CONFIRMED -> COMPLETED (version 2.0) ---------------------
def test_admin_completes_started_rental_and_frees_the_slot(client, customer_headers,
                                                           other_headers, admin_headers,
                                                           car, clock):
    rid = _create_and_confirm(client, customer_headers, admin_headers, car.id)
    clock.now = datetime(2030, 1, 8, 9, 0)  # rental started, car returned a day early
    response = client.post(f"/reservations/{rid}/complete", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"
    # COMPLETED does not block the car any more
    later = _create(client, other_headers, car.id, start="2030-01-08T10:00",
                    end="2030-01-08T12:00")
    assert later.status_code == 201


def test_cannot_complete_before_pickup_or_twice(client, customer_headers, admin_headers,
                                                car, clock):
    rid = _create_and_confirm(client, customer_headers, admin_headers, car.id)
    early = client.post(f"/reservations/{rid}/complete", headers=admin_headers)
    assert early.status_code == 409
    assert early.json()["detail"] == "Auto ještě nebylo vyzvednuto, rezervaci nelze ukončit"

    clock.now = datetime(2030, 1, 7, 10, 0)
    assert client.post(f"/reservations/{rid}/complete", headers=admin_headers).status_code == 200
    again = client.post(f"/reservations/{rid}/complete", headers=admin_headers)
    assert again.status_code == 409
    cancel = client.post(f"/reservations/{rid}/cancel", headers=admin_headers)
    assert cancel.status_code == 409
    assert cancel.json()["detail"] == "Auto už bylo vráceno"


def test_draft_cannot_be_completed(client, customer_headers, admin_headers, car):
    rid = _create(client, customer_headers, car.id).json()["id"]
    response = client.post(f"/reservations/{rid}/complete", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Rezervaci ve stavu DRAFT nelze ukončit"


def test_customer_cannot_complete(client, customer_headers, admin_headers, car, clock):
    rid = _create_and_confirm(client, customer_headers, admin_headers, car.id)
    clock.now = datetime(2030, 1, 7, 10, 0)
    assert client.post(f"/reservations/{rid}/complete",
                       headers=customer_headers).status_code == 403


# --- UC6 / UC10 --------------------------------------------------------------
def test_my_reservations_only_own_newest_first(client, customer_headers, other_headers,
                                               car, cars, clock):
    first = _create(client, customer_headers, car.id).json()["id"]
    clock.now = datetime(2030, 1, 7, 7, 5)
    second = _create(client, customer_headers, cars[1].id).json()["id"]
    _create(client, other_headers, cars[2].id)

    response = client.get("/reservations/me", headers=customer_headers)
    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [second, first]


def test_all_reservations_admin_only(client, customer_headers, other_headers, admin_headers,
                                     car, cars, clock):
    _create(client, customer_headers, car.id)
    clock.now = datetime(2030, 1, 7, 7, 5)
    newest = _create(client, other_headers, cars[1].id).json()["id"]

    forbidden = client.get("/reservations/", headers=customer_headers)
    assert forbidden.status_code == 403

    response = client.get("/reservations/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == newest
    assert {"car", "user", "start_date", "end_date", "total_price", "payment_method",
            "status"} <= data[0].keys()
    assert data[0]["user"]["email"] == "other@test.cz"


def test_reservation_row_in_database(client, customer_headers, car, db):
    rid = _create(client, customer_headers, car.id).json()["id"]
    db.expire_all()
    row = db.get(Reservation, rid)
    assert row.status == "DRAFT"
    assert row.start_date == datetime(2030, 1, 7, 9, 0)
    assert row.created_at is not None
