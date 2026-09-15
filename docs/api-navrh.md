# Návrh API

Backend po spuštění publikuje interaktivní OpenAPI dokumentaci na
`http://localhost:8000/docs` (Swagger UI) a `http://localhost:8000/redoc` —
ty jsou zdrojem pravdy pro přesná schémata. Tento dokument je jejich čitelný
přehled pro účely dokumentace SI.

## Auta

| Metoda | Cesta | Popis | Odpovědi |
|---|---|---|---|
| GET | `/cars/` | Seznam všech aut | 200 |
| GET | `/cars/{car_id}` | Detail jednoho auta | 200, 404 |
| POST | `/cars/` | Založení nového auta | 201, 422 |

### Schéma `Car`

```json
{
  "id": 1,
  "brand": "Škoda",
  "model": "Octavia",
  "year": 2022,
  "license_plate": "1AB2345",
  "daily_price": 890.0
}
```

### Dostupnost

| Metoda | Cesta | Popis | Odpovědi |
|---|---|---|---|
| GET | `/cars/{car_id}/availability?start_date=...&end_date=...` | Je auto v daném termínu volné? (na základě CONFIRMED rezervací) | 200, 404, 422 |

## Rezervace

Rezervace má stav `DRAFT` → `CONFIRMED` / `CANCELLED` (viz
[domenovy-model.md](domenovy-model.md) a [intent-and-change.md](intent-and-change.md)).

| Metoda | Cesta | Popis | Odpovědi |
|---|---|---|---|
| GET | `/reservations/` | Seznam všech rezervací | 200 |
| POST | `/reservations/` | Vytvoření rezervace (stav `DRAFT`) | 201, 404 (auto neexistuje), 409 (termín obsazen CONFIRMED rezervací), 422 (neplatná data) |
| POST | `/reservations/{id}/confirm` | Potvrzení rezervace (`DRAFT → CONFIRMED`), odešle notifikaci | 200, 404, 409 (už není DRAFT, nebo termín mezitím obsadila jiná rezervace) |
| POST | `/reservations/{id}/cancel` | Zrušení rezervace (`→ CANCELLED`) | 200, 404, 409 (už zrušena, nebo potvrzená rezervace už začala) |

## Uživatelé

| Metoda | Cesta | Popis | Odpovědi |
|---|---|---|---|
| GET | `/users/` | Seznam uživatelů (vznikají automaticky při vytvoření rezervace) | 200 |
| GET | `/users/{id}` | Detail uživatele | 200, 404 |

### Schéma `ReservationCreate` (request)

`customer_name`/`customer_email` slouží k nalezení nebo založení `User`
záznamu (`get_or_create_user`) — bez nutnosti se předem registrovat.

```json
{
  "car_id": 1,
  "customer_name": "Jan Novák",
  "customer_email": "jan.novak@example.com",
  "start_date": "2026-10-01T00:00:00",
  "end_date": "2026-10-05T00:00:00"
}
```

### Schéma `Reservation` (response)

```json
{
  "id": 1,
  "car_id": 1,
  "user_id": 1,
  "status": "DRAFT",
  "start_date": "2026-10-01T00:00:00",
  "end_date": "2026-10-05T00:00:00",
  "created_at": "2026-09-15T14:48:01.489531"
}
```

## Chybové odpovědi

Všechny chyby mají tvar `{"detail": "popis chyby"}` (FastAPI konvence),
u validačních chyb (422) `detail` obsahuje pole s popisem chybných vstupů.

## Plánované endpointy (další iterace)

| Metoda | Cesta | Popis |
|---|---|---|
| POST | `/auth/register`, `/auth/login` | Registrace a přihlášení uživatele |
| GET | `/reservations/me` | Rezervace přihlášeného zákazníka |
| PUT/PATCH | `/cars/{id}` | Úprava auta (admin) |
| DELETE | `/cars/{id}` | Odebrání auta (admin) |
