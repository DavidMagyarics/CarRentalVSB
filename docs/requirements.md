# Requirements Specification (SRS) — CarRentalVSB

Seminar project for the **Software Engineering** course — a car rental
reservation system.

## 1. Purpose and scope

The goal of the system is to let customers browse the rental's fleet and
book a vehicle for a chosen date and time, and to let the rental admin
manage the fleet, review reservation requests and approve them.

The system is developed iteratively (see [roadmap.md](roadmap.md)) — this
document describes the **full scope** of the system as it stands today.
Every requirement below lists its implementation status; as of this
revision, every one of them is `Done` — there is nothing left in a `Planned`
state. The one piece of earlier-considered scope that will *not* be built,
a real payment provider integration, is intentionally not listed here at
all (see decision D9 in
[architecture-and-decisions.md](architecture-and-decisions.md) and
[roadmap.md](roadmap.md)) — the mock `payment_method` flag (F13) is the
final design, not a stand-in for it.

Status: `Done` — implemented and verified (automated tests and/or a manual
check recorded in the status note).

## 2. Actors

| Actor | Description |
|---|---|
| Customer | A registered user who wants to book a car. |
| Admin | A rental employee who manages the fleet and approves/cancels reservations. |
| System | Automated checks (e.g. car availability, opening hours, price calculation). |

## 3. Functional requirements

| ID | Requirement | Actor | Status |
|---|---|---|---|
| F1 | The customer can view the list of cars (brand, model, year, photo, price/day, price/hour, specs). | Customer | Done |
| F2 | The customer can create a reservation for a chosen car and pickup/return date & time; the reservation is created in `DRAFT` state. | Customer | Done |
| F3 | When creating and confirming a reservation, the system checks that the date range doesn't overlap another **confirmed** (`CONFIRMED`) reservation for the same car. | System | Done |
| F4 | Reservations belong to the logged-in customer's account (see F5) — no anonymous name/e-mail booking. | Customer | Done |
| F5 | Customer registration (account with hashed password) and login, issuing a JWT access token. | Customer | Done |
| F6 | The customer can view their own reservations and cancel any of them. | Customer | Done |
| F7 | The admin logs in through the same login as customers; the account's `role` (`ADMIN`) unlocks the administration tabs. | Admin | Done |
| F8 | The admin can add, edit and remove a car from the fleet; removing a car also removes all of its reservations. | Admin | Done |
| F9 | The admin sees an overview of all reservations (with customer contact info) and can confirm or cancel any of them. | Admin | Done |
| F10 | The system allows filtering cars by category, transmission, fuel type and price range. | Customer | Done |
| F11 | The system supports multiple rental branches. Every car belongs to one branch; the customer can see and filter by it. Pickup and return both happen at the car's own branch — cross-branch drop-off is not supported yet. | Customer | Done |
| F12 | The system notifies the customer when their reservation is confirmed, via the Notification Service. Defaults to a console log; sends a real e-mail automatically once SMTP settings are configured (no code change). | System | Done |
| F13 | The customer chooses a payment method (Cash or Card) when booking; Card shows a mock card-details step that is never sent to the server. | Customer | Done |
| F14 | The admin confirms a pending reservation (`DRAFT → CONFIRMED`); the system re-checks availability before confirming. **A customer cannot confirm their own reservation** — this is a deliberate domain rule, not a bug: a request only becomes binding once staff has approved it. | Admin | Done |
| F15 | The customer (own reservation) or admin (any reservation) can cancel a reservation (`→ CANCELLED`); a confirmed reservation can only be cancelled before the rental period starts (domain-specific rule). | Customer, Admin | Done |
| F16 | The customer can check a car's availability for a specific date range without creating a reservation (used internally while picking dates in the booking form). | Customer | Done |
| F17 | Each car has both a daily and an hourly price; the system bills full 24h blocks at the daily rate and the remainder at the hourly rate, capped at one more day's rate — a long partial day is never worse than booking a full day. | System | Done |
| F18 | The rental only operates Mon–Fri, 08:00–20:00 — pickup and return must both fall inside opening hours, since staff has to be present to hand over/receive the car. | System | Done (checked client-side *and* re-validated server-side; see N12) |
| F19 | The customer can reach support via a floating contact widget (dummy phone number and e-mail) visible on every page. | Customer | Done |

## 4. Non-functional requirements

| ID | Requirement | Status |
|---|---|---|
| N1 | The backend provides a REST API with automatically generated OpenAPI/Swagger documentation. | Done |
| N2 | The application is split into a separate backend (API) and frontend (SPA), communicating over HTTP/JSON. | Done |
| N3 | The backend is covered by automated tests (unit/integration) run via `pytest`. | Done (40 tests) |
| N4 | The code is versioned in Git; each feature was developed on a separate branch and integrated into `main` through a pull request (PRs #2–#7). Later, smaller documentation-only changes are pushed directly to `main`. | Done |
| N5 | The system validates input data (types, required fields, e-mail format, password length, start/end date consistency). | Done |
| N6 | The API responds to common requests (reading the car list) within 300 ms in a local environment. | Done (measured: `GET /cars/` over 20 requests on localhost/SQLite — avg. 7 ms, max 20 ms once warmed up; ~80 ms on the very first, cold-start request) |
| N7 | User passwords are stored hashed (bcrypt), never in plain text. | Done |
| N8 | The application is responsive and usable on mobile devices. | Done (one breakpoint at 720px; verified at desktop and ~420px widths, not exhaustively tested on real devices) |
| N9 | Deployment via containers (Docker) for easy setup on another machine. | Done (`docker compose up --build`; `backend/Dockerfile`, `frontend/Dockerfile` — nginx serving the Vite build — and `docker-compose.yml`; verified end-to-end: login, browse, reserve, confirm, notification logged) |
| N10 | Authentication uses stateless JWT bearer tokens (no server-side session storage). | Done |
| N11 | Sending a real confirmation e-mail requires no code change — only environment variables (`backend/.env`, see `.env.example`); the app runs correctly without them (logs instead). | Done |
| N12 | Opening-hours validation (F18) is re-validated server-side on every reservation `POST /reservations/` makes (`schemas.ReservationCreate.within_business_hours`), not just client-side — a request made directly against the API without going through the frontend is still rejected (422) outside Mon–Fri 08:00–20:00. It still assumes a single timezone throughout the system (see §5); true per-customer timezone handling remains out of scope. | Done |

## 5. Constraints and assumptions

- Target platform: modern web browser (desktop and mobile).
- Backend: Python / FastAPI, SQLite database for development (with the option to move to PostgreSQL in production).
- Frontend: React + TypeScript (Vite).
- The project is built as part of a course — the emphasis is on following
  the software engineering process (requirements → design → implementation →
  testing → documentation), not on production-grade scalability.
- Single timezone assumed throughout (no per-user timezone handling yet — see N12).

## 6. Glossary

| Term | Meaning |
|---|---|
| Reservation | A customer's commitment to rent a specific car for a specific date & time range, with a status, a computed price and a payment method. |
| Availability | A car is available for a date range if it doesn't overlap another `CONFIRMED` reservation. |
| Fleet | The set of all cars registered in the system. |
| Branch | A physical pickup/return location; every car belongs to exactly one (F11). |
| Confirm | The admin-only action that turns a `DRAFT` reservation into a binding `CONFIRMED` one. |
