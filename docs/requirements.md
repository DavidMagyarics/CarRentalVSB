# Requirements Specification (SRS) — CarRentalVSB

Seminar project for the **Software Engineering** course — a car rental
reservation system.

## 1. Purpose and scope

The goal of the system is to let customers browse the rental's fleet and
book a vehicle for a chosen date range, and to let the rental admin manage
the fleet and the reservation overview.

The system is developed iteratively (see [roadmap.md](roadmap.md)) — this
document describes the **target scope** of the whole system. Each
requirement lists its implementation status.

Statuses: `MVP` (done), `Planned` (to be added in later iterations).

## 2. Actors

| Actor | Description |
|---|---|
| Customer | An unregistered or registered user who wants to book a car. |
| Admin | A rental employee who manages the fleet and reservations. |
| System | Automated checks (e.g. car availability for a date range). |

## 3. Functional requirements

| ID | Requirement | Actor | Status |
|---|---|---|---|
| F1 | The customer can view the list of available cars (brand, model, year, price/day). | Customer | MVP |
| F2 | The customer can create a reservation for a chosen car and date range (from–to); the reservation is created in `DRAFT` state. | Customer | MVP |
| F3 | When creating and confirming a reservation, the system checks that the date range doesn't overlap another **confirmed** (`CONFIRMED`) reservation for the same car. | System | MVP |
| F4 | The customer enters a name and email when reserving; the system finds or creates a `User` by email. | Customer | MVP |
| F5 | Customer registration and login (account, reservation history). | Customer | Planned |
| F6 | The customer can view and cancel their reservation. | Customer | Planned (backend `cancel` done, listing "my" reservations waits on F5) |
| F7 | The admin can log in to the administration area. | Admin | Planned |
| F8 | The admin can add, edit and remove a car from the fleet. | Admin | Planned |
| F9 | The admin sees an overview of all reservations and can cancel/confirm a reservation. | Admin | Planned |
| F10 | The system allows filtering cars by category, price and availability for a date range. | Customer | Planned |
| F11 | The system supports multiple rental branches (pickup/return). | Customer | Planned |
| F12 | The system sends the customer a notification when a reservation is confirmed, via the Notification Service. | System | MVP (stub) |
| F13 | The system supports a (mock) payment for a reservation. | Customer | Planned |
| F14 | The customer can confirm their reservation (`DRAFT → CONFIRMED`); the system re-checks availability before confirming. | Customer | MVP |
| F15 | The customer can cancel their reservation (`→ CANCELLED`); a confirmed reservation can only be cancelled before the rental period starts (domain-specific rule). | Customer | MVP |
| F16 | The customer can check a car's availability for a specific date range without creating a reservation. | Customer | MVP |

## 4. Non-functional requirements

| ID | Requirement | Status |
|---|---|---|
| N1 | The backend provides a REST API with automatically generated OpenAPI/Swagger documentation. | MVP |
| N2 | The application is split into a separate backend (API) and frontend (SPA), communicating over HTTP/JSON. | MVP |
| N3 | The backend is covered by automated tests (unit/integration) run via `pytest`. | MVP |
| N4 | The code is versioned in Git, development happens on separate branches with pull requests. | MVP |
| N5 | The system validates input data (types, required fields, email format, start/end date consistency). | MVP |
| N6 | The API responds to common requests (reading the car list) within 300 ms in a local environment. | Planned |
| N7 | User passwords (once authentication is introduced) are stored hashed (e.g. bcrypt), never in plain text. | Planned |
| N8 | The application is responsive and usable on mobile devices. | Planned |
| N9 | Deployment via containers (Docker) for easy setup on another machine. | Planned |

## 5. Constraints and assumptions

- Target platform: modern web browser (desktop and mobile).
- Backend: Python / FastAPI, SQLite database for development (with the option to move to PostgreSQL in production).
- Frontend: React + TypeScript (Vite).
- The project is built as part of a course — the emphasis is on following
  the software engineering process (requirements → design → implementation →
  testing → documentation), not on production-grade scalability.

## 6. Glossary

| Term | Meaning |
|---|---|
| Reservation | A customer's commitment to rent a specific car for a specific date range. |
| Availability | A car is available for a date range if it doesn't overlap another existing reservation. |
| Fleet | The set of all cars registered in the system. |
