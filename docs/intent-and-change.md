# Project Frame

## Reservation domain

Car rental reservation system. The reserved resource is a specific **car**
in the fleet (identified among other things by its license plate).

## Purpose

The system serves rental customers who want to check car availability online
and create/confirm/cancel a reservation for a specific date range, and the
rental operator who manages the fleet and the reservation overview.

## Users / Stakeholders

- **Customer** — browses the fleet, creates, confirms and cancels their reservations.
- **Rental Admin** — manages the fleet and oversees reservations (planned in later iterations).
- **Notification Service** (external system) — informs the customer when a reservation is confirmed.

## Core concepts

- **Reservation** — a link between a resource, a user and a time slot, with a status.
- **Resource / Car** — a specific car in the fleet (brand, model, year, license plate, price/day).
- **User** — the person who creates the reservation (name, email).

## Core operations

- Create reservation
- Confirm reservation
- Cancel reservation
- Check availability

Implemented as a REST API:

| Operation | Endpoint |
|---|---|
| Create reservation | `POST /reservations/` |
| Confirm reservation | `POST /reservations/{id}/confirm` |
| Cancel reservation | `POST /reservations/{id}/cancel` |
| Check availability | `GET /cars/{car_id}/availability?start_date=...&end_date=...` |

## Persistent state

**Car (resource):** id, brand, model, year, license_plate, daily_price.

**User:** id, name, email.

**Reservation:** id, car_id (FK → Car), user_id (FK → User), status
(DRAFT/CONFIRMED/CANCELLED), start_date, end_date, created_at.

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

## Domain-specific business rule

**A confirmed (CONFIRMED) reservation can only be cancelled before the rental
period starts (`start_date` must be in the future).** Once the rental period
has started according to `start_date`, the customer can no longer cancel it
through the system — it has to be handled operationally (physical return /
complaint), not by automatically cancelling the reservation, so that the
record of a car that is actually out of the lot doesn't just "disappear".

Implemented in `crud.cancel_reservation`, tested in
`test_cannot_cancel_confirmed_reservation_after_start_date`.

## External / system boundary

**Notification Service** — when a reservation is confirmed (`confirm`), the
system calls `NotificationService.send_confirmation(reservation, user)`
(`backend/app/notification.py`). For development, `LoggingNotificationService`
is wired in (simulates a successful send and logs it); in production this
would be a real email/SMS gateway. The interface is designed so the
implementation can be swapped without changing the domain code — see
[architecture-and-decisions.md](architecture-and-decisions.md).

## Assumption

We assume that at this stage it's enough to identify the customer by name
and email without login (authentication) — the system finds or creates the
`User` by email itself (`get_or_create_user`). This assumption goes away once
registration/login is added (F5/F7 in `docs/requirements.md`).

## Unknown

We don't yet know exactly what the real integration with the Notification
Service will look like (which provider, sync vs. async/queue, how to handle
an outage) — this is intentionally left open as a future engineering spike
(variant B — boundary failure).

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
