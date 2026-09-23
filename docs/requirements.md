# Requirements Specification (SRS) — CarRentalVSB

Seminar project for the **Software Engineering** course — a car rental
reservation system.

## 1. Purpose and scope

The goal of the system is to let customers browse the rental's fleet and
book a vehicle for a chosen date and time, and to let the rental admin
manage the fleet, review reservation requests and approve them.

The system is developed iteratively (see [roadmap.md](roadmap.md)) — this
document describes the **target scope** of the whole system. Each
requirement lists its implementation status.

Statuses: `MVP` (done), `Planned` (to be added in later iterations).

## 2. Actors

| Actor | Description |
|---|---|
| Customer | A registered user who wants to book a car. |
| Admin | A rental employee who manages the fleet and approves/cancels reservations. |
| System | Automated checks (e.g. car availability, opening hours, price calculation). |

## 3. Functional requirements

| ID | Requirement | Actor | Status |
|---|---|---|---|
| F1 | The customer can view the list of cars (brand, model, year, photo, price/day, price/hour, specs). | Customer | MVP |
| F2 | The customer can create a reservation for a chosen car and pickup/return date & time; the reservation is created in `DRAFT` state. | Customer | MVP |
| F3 | When creating and confirming a reservation, the system checks that the date range doesn't overlap another **confirmed** (`CONFIRMED`) reservation for the same car. | System | MVP |
| F4 | Reservations belong to the logged-in customer's account (see F5) — no anonymous name/e-mail booking. | Customer | MVP |
| F5 | Customer registration (account with hashed password) and login, issuing a JWT access token. | Customer | MVP |
| F6 | The customer can view their own reservations and cancel any of them. | Customer | MVP |
| F7 | The admin logs in through the same login as customers; the account's `role` (`ADMIN`) unlocks the administration tabs. | Admin | MVP |
| F8 | The admin can add, edit and remove a car from the fleet. | Admin | MVP |
| F9 | The admin sees an overview of all reservations (with customer contact info) and can confirm or cancel any of them. | Admin | MVP |
| F10 | The system allows filtering cars by category, transmission, fuel type and price range. | Customer | MVP |
| F11 | The system supports multiple rental branches (pickup/return). | Customer | Planned |
| F12 | The system notifies the customer when their reservation is confirmed, via the Notification Service. Defaults to a console log; sends a real e-mail automatically once SMTP settings are configured (no code change). | System | MVP |
| F13 | The customer chooses a payment method (Cash or Card) when booking; Card shows a mock card-details step that is never sent to the server. | Customer | MVP |
| F14 | The admin confirms a pending reservation (`DRAFT → CONFIRMED`); the system re-checks availability before confirming. **A customer cannot confirm their own reservation** — this is a deliberate domain rule, not a bug: a request only becomes binding once staff has approved it. | Admin | MVP |
| F15 | The customer (own reservation) or admin (any reservation) can cancel a reservation (`→ CANCELLED`); a confirmed reservation can only be cancelled before the rental period starts (domain-specific rule). | Customer, Admin | MVP |
| F16 | The customer can check a car's availability for a specific date range without creating a reservation (used internally while picking dates in the booking form). | Customer | MVP |
| F17 | Each car has both a daily and an hourly price; the system bills full 24h blocks at the daily rate and the remainder at the hourly rate, capped at one more day's rate — a long partial day is never worse than booking a full day. | System | MVP |
| F18 | The rental only operates Mon–Fri, 08:00–20:00 — pickup and return must both fall inside opening hours, since staff has to be present to hand over/receive the car. | System | MVP (checked client-side; see N12) |
| F19 | The customer can reach support via a floating contact widget (dummy phone number and e-mail) visible on every page. | Customer | MVP |

## 4. Non-functional requirements

| ID | Requirement | Status |
|---|---|---|
| N1 | The backend provides a REST API with automatically generated OpenAPI/Swagger documentation. | MVP |
| N2 | The application is split into a separate backend (API) and frontend (SPA), communicating over HTTP/JSON. | MVP |
| N3 | The backend is covered by automated tests (unit/integration) run via `pytest`. | MVP (40 tests) |
| N4 | The code is versioned in Git, development happens on separate branches with pull requests. | MVP |
| N5 | The system validates input data (types, required fields, e-mail format, password length, start/end date consistency). | MVP |
| N6 | The API responds to common requests (reading the car list) within 300 ms in a local environment. | Planned (not measured) |
| N7 | User passwords are stored hashed (bcrypt), never in plain text. | MVP |
| N8 | The application is responsive and usable on mobile devices. | MVP (one breakpoint at 720px; verified at desktop and ~420px widths, not exhaustively tested on real devices) |
| N9 | Deployment via containers (Docker) for easy setup on another machine. | Planned |
| N10 | Authentication uses stateless JWT bearer tokens (no server-side session storage). | MVP |
| N11 | Sending a real confirmation e-mail requires no code change — only environment variables (`backend/.env`, see `.env.example`); the app runs correctly without them (logs instead). | MVP |
| N12 | Opening-hours validation (F18) is enforced client-side only; the backend does not yet re-validate it, since it doesn't track the customer's timezone. A known, recorded limitation, not an oversight. | Planned |

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
| Confirm | The admin-only action that turns a `DRAFT` reservation into a binding `CONFIRMED` one. |
