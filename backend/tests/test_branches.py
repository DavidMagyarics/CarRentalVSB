from tests.helpers import auth_headers, create_branch, create_car, make_admin, register


def test_create_and_list_branches(client):
    admin = make_admin(client)
    branch = create_branch(client, admin["access_token"], name="Ostrava")

    response = client.get("/branches/")

    assert response.status_code == 200
    branches = response.json()
    assert len(branches) == 1
    assert branches[0]["id"] == branch["id"]
    assert branches[0]["name"] == "Ostrava"


def test_get_branch_not_found(client):
    response = client.get("/branches/999")
    assert response.status_code == 404


def test_create_branch_requires_admin(client):
    user = register(client)
    response = client.post(
        "/branches/",
        json={"name": "X", "address": "Y"},
        headers=auth_headers(user["access_token"]),
    )
    assert response.status_code == 403


def test_update_branch(client):
    admin = make_admin(client)
    branch = create_branch(client, admin["access_token"])

    response = client.put(
        f"/branches/{branch['id']}",
        json={"name": "Nový název"},
        headers=auth_headers(admin["access_token"]),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Nový název"


def test_delete_branch(client):
    admin = make_admin(client)
    branch = create_branch(client, admin["access_token"])

    response = client.delete(
        f"/branches/{branch['id']}", headers=auth_headers(admin["access_token"])
    )

    assert response.status_code == 204
    assert client.get(f"/branches/{branch['id']}").status_code == 404


def test_cannot_delete_branch_with_cars(client):
    admin = make_admin(client)
    branch = create_branch(client, admin["access_token"])
    create_car(client, admin["access_token"], branch_id=branch["id"])

    response = client.delete(
        f"/branches/{branch['id']}", headers=auth_headers(admin["access_token"])
    )

    assert response.status_code == 409


def test_create_car_with_unknown_branch_returns_404(client):
    admin = make_admin(client)

    response = client.post(
        "/cars/",
        json={
            "brand": "X",
            "model": "Y",
            "year": 2020,
            "license_plate": "Z9",
            "daily_price": 100,
            "hourly_price": 10,
            "branch_id": 999,
        },
        headers=auth_headers(admin["access_token"]),
    )

    assert response.status_code == 404


def test_car_response_includes_nested_branch(client):
    admin = make_admin(client)
    branch = create_branch(client, admin["access_token"], name="Praha")
    car = create_car(client, admin["access_token"], branch_id=branch["id"])

    assert car["branch"]["id"] == branch["id"]
    assert car["branch"]["name"] == "Praha"


def test_filter_cars_by_branch(client):
    admin = make_admin(client)
    branch_a = create_branch(client, admin["access_token"], name="A")
    branch_b = create_branch(client, admin["access_token"], name="B")
    create_car(client, admin["access_token"], license_plate="9ZZ1001", branch_id=branch_a["id"])
    create_car(client, admin["access_token"], license_plate="9ZZ1002", branch_id=branch_b["id"])

    response = client.get("/cars/", params={"branch_id": branch_a["id"]})

    assert response.status_code == 200
    cars = response.json()
    assert len(cars) == 1
    assert cars[0]["license_plate"] == "9ZZ1001"
