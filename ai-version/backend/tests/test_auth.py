"""UC1 Register, UC2 Log in, JWT handling."""

from app.models import User


def test_register_creates_customer_and_returns_token(client, db):
    response = client.post(
        "/auth/register", json={"name": "Eva", "email": "Eva@Test.cz", "password": "heslo123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "CUSTOMER"
    assert body["user"]["email"] == "eva@test.cz"

    user = db.query(User).filter_by(email="eva@test.cz").one()
    assert user.password_hash != "heslo123"
    assert user.password_hash.startswith("$2")  # bcrypt
    assert user.check_password("heslo123")

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "eva@test.cz"


def test_register_duplicate_email_is_409(client):
    payload = {"name": "Eva", "email": "eva@test.cz", "password": "heslo123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    response = client.post("/auth/register", json={**payload, "email": "EVA@test.cz"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Tento e-mail je již zaregistrován"


def test_register_invalid_email_or_short_password_is_422(client):
    bad_email = client.post(
        "/auth/register", json={"name": "Eva", "email": "not-an-email", "password": "heslo123"}
    )
    assert bad_email.status_code == 422
    short = client.post(
        "/auth/register", json={"name": "Eva", "email": "eva@test.cz", "password": "12345"}
    )
    assert short.status_code == 422


def test_login_success_returns_token_and_role(client, admin_headers):
    response = client.post("/auth/login", json={"email": "admin@test.cz", "password": "admin123"})
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "ADMIN"


def test_login_wrong_password_and_unknown_email_are_401(client, customer_headers):
    wrong = client.post("/auth/login", json={"email": "customer@test.cz", "password": "nope!!"})
    unknown = client.post("/auth/login", json={"email": "nobody@test.cz", "password": "secret1"})
    for response in (wrong, unknown):
        assert response.status_code == 401
        assert response.json()["detail"] == "Nesprávný e-mail nebo heslo"


def test_protected_endpoint_without_or_with_bad_token_is_401(client):
    assert client.get("/reservations/me").status_code == 401
    bad = client.get("/reservations/me", headers={"Authorization": "Bearer garbage"})
    assert bad.status_code == 401
