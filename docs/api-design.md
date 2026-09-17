# API Design

Once running, the backend publishes interactive OpenAPI documentation at
`http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`
— these are the source of truth for the exact schemas. This document is a
readable overview of them for SWI documentation purposes.

## Cars

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/cars/` | List all cars | 200 |
| GET | `/cars/{car_id}` | Get a single car | 200, 404 |
| POST | `/cars/` | Create a new car | 201, 422 |

### `Car` schema

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

### Availability

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/cars/{car_id}/availability?start_date=...&end_date=...` | Is the car free for the given date range? (based on CONFIRMED reservations) | 200, 404, 422 |

## Reservations

A reservation has state `DRAFT` → `CONFIRMED` / `CANCELLED` (see
[domain-model.md](domain-model.md) and [intent-and-change.md](intent-and-change.md)).

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/reservations/` | List all reservations | 200 |
| POST | `/reservations/` | Create a reservation (state `DRAFT`) | 201, 404 (car doesn't exist), 409 (slot taken by a CONFIRMED reservation), 422 (invalid data) |
| POST | `/reservations/{id}/confirm` | Confirm a reservation (`DRAFT → CONFIRMED`), sends a notification | 200, 404, 409 (no longer DRAFT, or the slot was taken by another reservation in the meantime) |
| POST | `/reservations/{id}/cancel` | Cancel a reservation (`→ CANCELLED`) | 200, 404, 409 (already cancelled, or the confirmed reservation has already started) |

## Users

| Method | Path | Description | Responses |
|---|---|---|---|
| GET | `/users/` | List users (created automatically when a reservation is made) | 200 |
| GET | `/users/{id}` | Get a single user | 200, 404 |

### `ReservationCreate` schema (request)

`customer_name`/`customer_email` are used to find or create the `User`
record (`get_or_create_user`) — no need to register beforehand.

```json
{
  "car_id": 1,
  "customer_name": "Jan Novák",
  "customer_email": "jan.novak@example.com",
  "start_date": "2026-10-01T00:00:00",
  "end_date": "2026-10-05T00:00:00"
}
```

### `Reservation` schema (response)

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

## Error responses

All errors have the shape `{"detail": "error description"}` (FastAPI
convention); for validation errors (422), `detail` contains a field-by-field
description of the invalid input.

## Planned endpoints (future iterations)

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register`, `/auth/login` | User registration and login |
| GET | `/reservations/me` | Reservations of the logged-in customer |
| PUT/PATCH | `/cars/{id}` | Edit a car (admin) |
| DELETE | `/cars/{id}` | Remove a car (admin) |
