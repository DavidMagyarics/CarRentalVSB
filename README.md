# CarRentalVSB

Car rental reservation system — a seminar project for the **Software
Engineering** (SWI) course at VSB. A customer registers, browses and filters
the fleet, and books a car for a specific pickup/return date & time with a
chosen payment method; an admin reviews and approves (or cancels) requests
and manages the fleet. The system makes sure confirmed reservations on the
same car never overlap, and only bills for the time actually booked (hourly
rate, capped at the daily rate).

The project is built iteratively, week by week — the current scope and the
plan for upcoming increments are in [docs/roadmap.md](docs/roadmap.md).

## Team

| Name |
|---|
| David Magyarics |
| Filip Fajtl |
| Daniel Holík |
| František Hanák |

Repository: [github.com/DavidMagyarics/CarRentalVSB](https://github.com/DavidMagyarics/CarRentalVSB)

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, JWT auth (PyJWT + bcrypt)
- **Frontend:** React, TypeScript, Vite
- **Tests:** pytest (backend, 40 tests)

## Repository structure

```
backend/    FastAPI REST API
frontend/   React SPA
docs/       SWI documentation (requirements, use cases, architecture, ...)
```

## Documentation

| Document | Contents |
|---|---|
| [docs/intent-and-change.md](docs/intent-and-change.md) | **Project Frame** (SWI C01) + domain rules + selected future pressure |
| [docs/architecture-and-decisions.md](docs/architecture-and-decisions.md) | Architecture (C4), decision log, boundary, future pressure (SWI C01) |
| [docs/evidence-and-evolution.md](docs/evidence-and-evolution.md) | **C01 Engineering Spike** — evidence and decision |
| [docs/requirements.md](docs/requirements.md) | Requirements specification (SRS) |
| [docs/use-cases.md](docs/use-cases.md) | Use case specification — use case diagram + a table for every use case |
| [docs/activity-diagrams.md](docs/activity-diagrams.md) | Activity diagram of every use case |
| [docs/sequence-diagrams.md](docs/sequence-diagrams.md) | Sequence diagram of every use case |
| [docs/class-diagram.md](docs/class-diagram.md) | Class diagram |
| [docs/state-diagrams.md](docs/state-diagrams.md) | State diagrams (Reservation, ReservationForm) |
| [docs/design-patterns.md](docs/design-patterns.md) | Design pattern State applied to Reservation |
| [docs/deployment-diagram.md](docs/deployment-diagram.md) | Deployment diagram (nodes, containers, protocols) |
| [docs/architecture.md](docs/architecture.md) | Detailed architecture, repository structure, technology choices |
| [docs/domain-model.md](docs/domain-model.md) | ER / domain model |
| [docs/api-design.md](docs/api-design.md) | REST API design |
| [docs/testing-strategy.md](docs/testing-strategy.md) | Testing strategy |
| [docs/roadmap.md](docs/roadmap.md) | Weekly development plan |

## Running the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows (on Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs on `http://localhost:8000`, interactive docs at
`http://localhost:8000/docs`. On first run it creates the SQLite database
`carrental.db` with sample cars, a demo admin and a demo customer with a
couple of sample reservations (see **Demo accounts** below).

Real e-mail sending is optional — without any configuration, reservation
confirmations are just logged to the console. To send real e-mails, copy
`backend/.env.example` to `backend/.env` and fill in SMTP credentials (see
the comments in that file for a step-by-step Gmail example); no code change
is needed either way.

### Tests

```bash
cd backend
pytest -v
```

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs on `http://localhost:5173` and expects the backend at
`http://localhost:8000` (configurable via `.env`, see `.env.example`).

## Running with Docker

The whole app (backend + frontend) can also run in containers, without
installing Python or Node locally:

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000` (`/docs` for the OpenAPI UI)

The backend's SQLite database lives inside the container, not on a volume,
so it resets (reseeds the demo accounts and fleet) whenever the container is
recreated — fine for local demo use, matching the project's "SQLite for
development" scope (see `docs/requirements.md`). To send real confirmation
e-mails instead of just logging them, set the `SMTP_*` variables (see
`backend/.env.example`) in your shell or in a `.env` file next to
`docker-compose.yml` before running `docker compose up` — no code or image
change needed.

## Demo accounts

Seeded automatically on first backend run:

| Role | E-mail | Password |
|---|---|---|
| Admin | `admin@carrentalvsb.cz` | `admin123` |
| Customer | `jan.novak@example.com` | `heslo123` |

The admin account unlocks the "Fleet administration" and "All reservations"
tabs, where reservations get confirmed (see the domain-specific rule in
[docs/intent-and-change.md](docs/intent-and-change.md) — a customer cannot
confirm their own reservation).

## Walking skeleton

The end-to-end path proven by the C01 persistence spike and now fully wired
through the real frontend, not just the API:

```
Customer logs in → browses & filters cars → picks pickup/return date & time
→ system checks opening hours + availability → customer chooses a payment
method → POST /reservations (price computed server-side, state DRAFT)
→ admin reviews it under "All reservations" → confirms it
→ system re-checks availability, sets state CONFIRMED, sends a notification
→ customer sees the confirmed reservation under "My reservations"
```

See [docs/evidence-and-evolution.md](docs/evidence-and-evolution.md) for the
original persistence spike (data survives a process restart) and
[docs/activity-diagrams.md](docs/activity-diagrams.md) for the activity diagram of every step
above.

## Submission note

This README and the documentation in `docs/` are updated continuously as
features are added — they reflect the current state of the project, not just
the initial assignment.
