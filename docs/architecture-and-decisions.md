# Architecture and Decisions

## Overview (C4 — Context)

![C4 Context diagram](diagrams/context.puml)

*Diagram source: [diagrams/context.puml](diagrams/context.puml) — PlantUML, the image is automatically re-rendered on every source change (see [.github/workflows/render-plantuml.yml](../.github/workflows/render-plantuml.yml)).*

## Containers (C4 — Container)

![C4 Container diagram](diagrams/container.puml)

*Diagram source: [diagrams/container.puml](diagrams/container.puml).*

A more detailed breakdown of the repository structure and backend layering is
in [architecture.md](architecture.md) (written in the first iteration of the
project, its content remains valid). This document additionally contains the
decision log, the boundary description and the future pressure selected for
the C01 assignment.

## External / system boundary: Notification Service

The domain depends on the Notification Service through a small
`NotificationService` interface (`backend/app/notification.py`):

```python
class NotificationService(Protocol):
    def send_confirmation(self, reservation, user) -> bool: ...
```

Two implementations now exist: `LoggingNotificationService` (default, logs
only) and `EmailNotificationService` (real SMTP send via the standard-library
`smtplib` — no new dependency). `main.py` picks whichever one applies at
startup based on whether `SMTP_HOST` is set in the environment (see
`backend/.env.example`), with no change to domain code in `crud.py`/routers —
exactly the swap this boundary was designed to allow. Behavior on failure of
this service (timeout, 5xx, retry) is still not handled beyond a caught
exception + log — see `Unknown` in [intent-and-change.md](intent-and-change.md).

## Decision log

| # | Decision | Rationale |
|---|---|---|
| D1 | Backend: FastAPI + SQLAlchemy + SQLite (dev) | Automatic OpenAPI docs, type validation via Pydantic, zero DB configuration for a school project; easy migration to PostgreSQL without ORM code changes. |
| D2 | Frontend: React + TypeScript (Vite) | Component model matches the domain concepts (car list, reservation form); fast dev server. |
| D3 | Reservation has an explicit state (`DRAFT`/`CONFIRMED`/`CANCELLED`) instead of being "done" right away | The C01 assignment requires meaningful states and confirm/cancel operations; DRAFT also lets the customer reconsider without immediately blocking the slot for others. |
| D4 | The common overlap rule only applies to `CONFIRMED` reservations, not `DRAFT` | Two DRAFT reservations for the same slot can coexist (nobody has bindingly claimed it yet); it becomes binding only on confirmation — see `crud.is_car_available`. |
| D5 | Authentication is stateless JWT bearer tokens (bcrypt-hashed passwords), not sessions | No server-side session store to manage; the frontend just attaches `Authorization: Bearer <token>`. Superseded C01's original `get_or_create_user`-by-e-mail approach once real accounts were needed for admin/customer role separation. |
| D6 | The Notification Service is a system boundary with two swappable implementations (logging stub, real SMTP), chosen at startup by an environment variable | Keeps a real send available without requiring credentials to exist for the app to run; the domain/router code never changes when the implementation is swapped. |
| D7 | Confirming a reservation requires the `ADMIN` role; a customer can only cancel, never confirm, their own reservation | Correctness fix once real accounts existed: a request shouldn't become binding without staff approval — see domain-specific rule 2 in `intent-and-change.md`. |
| D8 | Reservation price is computed once server-side at creation (`crud.calculate_price`) and stored on the row, not recomputed on every read | Locks in the price the customer saw when booking even if the car's rates change later; also means the price shown in "My reservations" is guaranteed consistent with what was actually charged. |
| D9 | Payment method (`CASH`/`CARD`) is stored on the reservation; card details are never part of the API | A real payment integration is out of scope (F13 is intentionally a mock) — modelling it as a flag rather than skipping it keeps the domain honest about what's implemented vs. simulated. |
| D10 | Car photos are optional, self-hosted files (`frontend/public/cars/`) referenced by URL, with a generated SVG illustration as fallback | Avoids hot-linking or depending on an external image host at runtime; a car added by an admin without a photo still renders a reasonable card instead of a broken image. |

## Selected future pressure

See [intent-and-change.md](intent-and-change.md#selected-future-pressure) —
**Category: Q (Quality/Scale)**, specifically 10x higher concurrency when
confirming reservations and the race-condition risk in `is_car_available` /
`confirm_reservation` over SQLite without transactional locking. It is not
implemented in C01, only recorded as a known risk for a future iteration.
