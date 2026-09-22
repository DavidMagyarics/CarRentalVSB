from tests.helpers import auth_headers, register


def test_register_creates_customer(client):
    user = register(client)
    assert user["user"]["role"] == "CUSTOMER"
    assert "access_token" in user


def test_register_duplicate_email_fails(client):
    register(client)
    response = client.post(
        "/auth/register",
        json={"name": "Jiný", "email": "jan.novak@example.com", "password": "heslo123"},
    )
    assert response.status_code == 409


def test_register_requires_minimum_password_length(client):
    response = client.post(
        "/auth/register",
        json={"name": "Jan", "email": "short@example.com", "password": "abc"},
    )
    assert response.status_code == 422


def test_login_with_correct_credentials(client):
    register(client)
    response = client.post(
        "/auth/login", json={"email": "jan.novak@example.com", "password": "heslo123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client):
    register(client)
    response = client.post(
        "/auth/login", json={"email": "jan.novak@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_with_unknown_email_fails(client):
    response = client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "heslo123"}
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_rejects_garbage_token(client):
    response = client.get("/auth/me", headers=auth_headers("not-a-real-token"))
    assert response.status_code == 401


def test_me_returns_current_user(client):
    user = register(client)
    response = client.get("/auth/me", headers=auth_headers(user["access_token"]))
    assert response.status_code == 200
    assert response.json()["email"] == "jan.novak@example.com"
