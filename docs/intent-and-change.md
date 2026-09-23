# Project Frame

## Reservation domain

Car rental reservation system. The reserved resource is a specific **car**
in the fleet (identified among other things by its license plate).

## Purpose

The system serves rental customers who want to check car availability online
and create/confirm/cancel a reservation for a specific date range, and the
rental operator who manages the fleet and the reservation overview.

## Users / Stakeholders

- **Customer** — registers/logs in, browses and filters the fleet, creates and cancels their own reservations, chooses a payment method.
- **Rental Admin** — logs in with the same mechanism (role-gated), manages the fleet (add/edit/remove cars), and is the only actor who can confirm a reservation.
- **Notification Service** (external system) — informs the customer when a reservation is confirmed.

## Core concepts

- **Reservation** — a link between a resource, a user and a time slot, with a status, a server-computed price and a payment method.
- **Resource / Car** — a specific car in the fleet (brand, model, year, license plate, daily and hourly price, category, transmission, fuel type, seats, optional photo).
- **User** — a registered account (name, email, hashed password, role: `CUSTOMER` or `ADMIN`) authenticated via JWT.

## Core operations

- Register / Log in
- Browse & filter cars
- Create reservation (includes: check availability, choose payment method)
- Confirm reservation (**admin-only**)
- Cancel reservation (owner or admin)
- Manage fleet (**admin-only**)

Implemented as a REST API — see [api-design.md](api-design.md) for the full
endpoint list; the reservation-lifecycle ones:

| Operation | Endpoint |
|---|---|
| Create reservation | `POST /reservations/` |
| Confirm reservation | `POST /reservations/{id}/confirm` (admin) |
| Cancel reservation | `POST /reservations/{id}/cancel` |
| Check availability | `GET /cars/{car_id}/availability?start_date=...&end_date=...` |

## Persistent state

**Car (resource):** id, brand, model, year, license_plate, daily_price,
hourly_price, category, transmission, fuel_type, seats, description,
image_url.

**User:** id, name, email, password_hash, role.

**Reservation:** id, car_id (FK → Car), user_id (FK → User), status
(DRAFT/CONFIRMED/CANCELLED), start_date, end_date, total_price,
payment_method, created_at.

## State-changing operation

`DRAFT → CONFIRMED` via `POST /reservations/{id}/confirm` (the system
re-checks car availability and sends a confirmation notification to the
customer through the Notification Service). Also `DRAFT → CANCELLED` and
`CONFIRMED → CANCELLED` via `POST /reservations/{id}/cancel`.

## Common business rule

Confirmed reservations for the same resource must not overlap.

Enforced in `crud.is_car_available`: it only checks against reservations in
`CONFIRMED` state for that car. The check runs both on `create` (you can't
create a reservation on a slot already confirmed by another reservation) and
on `confirm` (resolves a race between two DRAFT reservations on the same
slot — only one can be confirmed).

## Domain-specific business rules

**1. A confirmed (CONFIRMED) reservation can only be cancelled before the
rental period starts (`start_date` must be in the future).** Once the rental
period has started according to `start_date`, the customer can no longer
cancel it through the system — it has to be handled operationally (physical
return / complaint), not by automatically cancelling the reservation, so
that the record of a car that is actually out of the lot doesn't just
"disappear".

Implemented in `crud.cancel_reservation`, tested in
`test_cannot_cancel_confirmed_reservation_after_start_date`.

**2. Confirming a reservation is admin-only — a customer cannot approve
their own request.** A `DRAFT` reservation is the customer's *request*, not
a done deal; someone at the rental has to verify it (availability, payment)
before it becomes binding. This mirrors how the physical handover works: the
system shouldn't let a booking become real without a person at the counter
agreeing to it.

Implemented as a `require_admin` dependency on `POST
/reservations/{id}/confirm` (`routers/reservations.py`), tested in
`test_customer_cannot_confirm_own_reservation` and
`test_admin_can_confirm_any_reservation`.

**3. The rental only operates Mon–Fri, 08:00–20:00 — pickup and return must
both fall inside those hours,** because staff has to physically hand over
and receive the car. Enforced client-side in `ReservationForm.tsx`
(`isWithinBusinessHours`); not yet re-validated server-side (see N12 in
`requirements.md` — the backend doesn't track the customer's timezone, so a
naive server-side check would be wrong rather than merely redundant).

## External / system boundary

**Notification Service** — when a reservation is confirmed (`confirm`), the
system calls `NotificationService.send_confirmation(reservation, user)`
(`backend/app/notification.py`). Two implementations exist behind the same
interface: `LoggingNotificationService` (default — logs it, no real send)
and `EmailNotificationService` (real SMTP send via `smtplib`, no extra
dependency). Which one is used is decided once, at startup, based on whether
`SMTP_HOST` is set (see `backend/.env.example`) — swapping the real
implementation in required no domain-code change, exactly as designed in
[architecture-and-decisions.md](architecture-and-decisions.md).

## Assumption

Authentication is stateless JWT bearer tokens with no server-side session
store or refresh-token flow — acceptable for a seminar project's scope and
lifetime, but a real deployment would want token expiry/refresh and
revocation, neither of which exist yet.

## Unknown

We don't yet know exactly how the opening-hours rule (domain rule 3 above)
should be enforced server-side once customers might be in different
timezones — today it's a client-only check. This is intentionally left open
as a candidate for a future engineering spike.

---

## Selected future pressure

**Category:** Q — Quality / Scale

**Concrete pressure:** 10x more concurrent reservations (e.g. a promotion or
several branches at once generating significantly higher traffic on `POST
/reservations/` and `POST /reservations/{id}/confirm` at the same time for
the same cars).

**Why it is relevant to our reservation system:** The availability check
(`is_car_available`) and the DRAFT → CONFIRMED transition currently run as
read-then-write over SQLite without explicit row locking or application-level
transaction isolation. At 10x concurrency there's a race-condition risk — two
confirmations for the same slot could go through almost simultaneously and
violate the `common business rule` (two CONFIRMED reservations overlapping).
This pressure is **not** addressed implementation-wise in C01, it's just
recorded as a known risk for a future iteration (will require either a
database unique/exclusion constraint, or a transaction with
`SELECT ... FOR UPDATE` after moving to PostgreSQL).
