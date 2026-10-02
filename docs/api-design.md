# API Design

Once running, the backend publishes interactive OpenAPI documentation at
`http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`
— these are the source of truth for the exact schemas. This document is a
readable overview of them for SWI documentation purposes.

## Authentication

All endpoints except `GET /cars/`, `GET /cars/{id}`, `GET /cars/{id}/availability`,
`GET /branches/`, `GET /branches/{id}`, `POST /auth/register` and
`POST /auth/login` require a JWT bearer token:

```
Authorization: Bearer <token>
```

Obtained from `POST /auth/register` or `POST /auth/login`. Endpoints marked
**admin** additionally require the token's user to have `role: ADMIN`.

| Method | Path | Description | Responses |
|---|---|---|---|
| POST | `/auth/register` | Create a customer account, returns a token | 201, 409 (e-mail taken), 422 (password too short, ...) |
| POST | `/auth/login` | Log in, returns a token | 200, 401 (wrong credentials) |
| GET | `/auth/me` | Get the current user (requires token) | 200, 401 |

### `UserRegister` schema (request)

```json
{
  "name": "Jan Novák",
  "email": "jan.novak@example.com",
  "password": "heslo123"
}
```

### `Token` schema (response of register/login)

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Jan Novák",
    "email": "jan.novak@example.com",
    "role": "CUSTOMER"
  }
}
```

## Branches (F11)

A branch is a physical pickup/return location; every car belongs to exactly
one (see [domain-model.md](domain-model.md)).

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/branches/` | List all branches | 200 |
| GET | `/branches/{branch_id}` | Get a single branch | 200, 404 |
| POST | `/branches/` | **Admin.** Create a branch | 201, 401, 403, 422 |
| PUT | `/branches/{branch_id}` | **Admin.** Update a branch (partial) | 200, 401, 403, 404 |
| DELETE | `/branches/{branch_id}` | **Admin.** Remove a branch | 204, 401, 403, 404, 409 (cars still assigned to it) |

### `Branch` schema

```json
{
  "id": 1,
  "name": "Ostrava – centrum",
  "address": "28. října 15, Ostrava"
}
```

## Cars

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/cars/` | List cars, optionally filtered | 200 |
| GET | `/cars/{car_id}` | Get a single car | 200, 404 |
| POST | `/cars/` | **Admin.** Create a new car | 201, 401, 403, 404 (unknown `branch_id`), 422 |
| PUT | `/cars/{car_id}` | **Admin.** Update a car (partial) | 200, 401, 403, 404 (unknown car or `branch_id`) |
| DELETE | `/cars/{car_id}` | **Admin.** Remove a car | 204, 401, 403, 404 |
| GET | `/cars/{car_id}/availability?start_date=...&end_date=...` | Is the car free for the given date range? (based on `CONFIRMED` reservations) | 200, 404, 422 |

### Query parameters for `GET /cars/`

All optional, combinable: `category`, `transmission`, `fuel_type`,
`min_price`, `max_price`, `min_seats`, `branch_id`.

### `Car` schema

```json
{
  "id": 1,
  "brand": "Škoda",
  "model": "Octavia",
  "year": 2022,
  "license_plate": "1AB2345",
  "daily_price": 890.0,
  "hourly_price": 80.0,
  "category": "SEDAN",
  "transmission": "AUTOMATIC",
  "fuel_type": "PETROL",
  "seats": 5,
  "description": "Prostorný rodinný sedan s nízkou spotřebou a velkým kufrem.",
  "image_url": "/cars/skoda-octavia.jpg",
  "branch_id": 1,
  "branch": { "id": 1, "name": "Ostrava – centrum", "address": "28. října 15, Ostrava" }
}
```

`category` is one of `SEDAN | SUV | HATCHBACK | VAN | SPORTS`, `transmission`
is `MANUAL | AUTOMATIC`, `fuel_type` is `PETROL | DIESEL | ELECTRIC | HYBRID`.
`description` and `image_url` are optional (`null` when unset — the frontend
falls back to a category illustration when `image_url` is missing). `branch`
is nested the same way `car`/`user` are nested on a `Reservation`, so the
frontend doesn't need a separate lookup; `branch_id` must reference an
existing branch (SQLite doesn't enforce the foreign key itself, so the API
checks it explicitly).

## Reservations

A reservation has state `DRAFT` → `CONFIRMED` / `CANCELLED` (see
[domain-model.md](domain-model.md) and [intent-and-change.md](intent-and-change.md)).
Confirming is **admin-only** — a customer cannot approve their own request.

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/reservations/` | **Admin.** List every reservation | 200, 401, 403 |
| GET | `/reservations/me` | List the logged-in customer's own reservations | 200, 401 |
| POST | `/reservations/` | Create a reservation (state `DRAFT`) for the logged-in customer | 201, 401, 404 (car doesn't exist), 409 (slot taken by a `CONFIRMED` reservation), 422 (invalid data) |
| POST | `/reservations/{id}/confirm` | **Admin.** Confirm (`DRAFT → CONFIRMED`), sends a notification | 200, 401, 403, 404, 409 (no longer `DRAFT`, or the slot was taken in the meantime) |
| POST | `/reservations/{id}/cancel` | Cancel — owner or admin (`→ CANCELLED`) | 200, 401, 403 (not the owner and not an admin), 404, 409 (already cancelled, or a confirmed rental already started) |

### `ReservationCreate` schema (request)

The customer, car and price are derived server-side (from the JWT token, the
car's rates and the date range) — never trust client-sent values for these.

```json
{
  "car_id": 1,
  "start_date": "2026-10-01T09:00:00",
  "end_date": "2026-10-01T15:00:00",
  "payment_method": "CARD"
}
```

`payment_method` is `CASH` or `CARD`. Card details (number, expiry, CVC) are
never part of the API — the frontend's card form is a client-only mock step.

### `Reservation` schema (response)

The car and user are returned nested, so the frontend doesn't need a
separate lookup to render a reservation card/row.

```json
{
  "id": 1,
  "car_id": 1,
  "user_id": 1,
  "status": "DRAFT",
  "start_date": "2026-10-01T09:00:00",
  "end_date": "2026-10-01T15:00:00",
  "total_price": 420.0,
  "payment_method": "CARD",
  "created_at": "2026-09-15T14:48:01.489531",
  "car": { "id": 1, "brand": "Škoda", "model": "Octavia", "...": "..." },
  "user": { "id": 1, "name": "Jan Novák", "email": "jan.novak@example.com", "role": "CUSTOMER" }
}
```

`total_price` is computed once at creation by `crud.calculate_price` (full
24h blocks at `daily_price`, the remainder at `hourly_price` capped at one
more day's rate) and stored — it doesn't change if the car's price changes
later.

## Users

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/users/` | **Admin.** List all users | 200, 401, 403 |
| GET | `/users/{id}` | **Admin.** Get a single user | 200, 401, 403, 404 |

## Error responses

All errors have the shape `{"detail": "error description"}` (FastAPI
convention); for validation errors (422), `detail` contains a field-by-field
description of the invalid input. `401` means no/invalid token, `403` means
a valid token without the required role or ownership.
