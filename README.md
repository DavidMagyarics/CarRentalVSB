# CarRentalVSB

Car rental reservation system — a seminar project for the **Software
Engineering** (SWI) course at VSB. A customer browses the fleet, creates a
reservation, confirms or cancels it; the system makes sure confirmed
reservations on the same car never overlap.

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

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React, TypeScript, Vite
- **Tests:** pytest (backend)

## Repository structure

```
backend/    FastAPI REST API
frontend/   React SPA
docs/       SWI documentation (requirements, use cases, architecture, ...)
```

## Documentation

| Document | Contents |
|---|---|
| [docs/intent-and-change.md](docs/intent-and-change.md) | **Project Frame** (SWI C01) + selected future pressure |
| [docs/architecture-and-decisions.md](docs/architecture-and-decisions.md) | Architecture (C4), decision log, boundary, future pressure (SWI C01) |
| [docs/evidence-and-evolution.md](docs/evidence-and-evolution.md) | **C01 Engineering Spike** — evidence and decision |
| [docs/requirements.md](docs/requirements.md) | Requirements specification (SRS) |
| [docs/use-cases.md](docs/use-cases.md) | Use case diagram and specification |
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
`carrental.db` with a few sample cars.

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

## CP1 walking skeleton

An end-to-end path that will actually be runnable (frontend → backend → DB →
automated check) after C03 / before C04:

```
POST /reservations
→ validate      (car exists, end_date > start_date, slot not taken by a CONFIRMED reservation)
→ persist       (Reservation is created in DRAFT state, User is found/created by email)
→ return reservation ID  (+ status, car_id, user_id)
→ automated check  (pytest: GET /reservations/ returns the reservation with the same data)
```

The backend part of this flow is already implemented and tested in C01 (see
[docs/evidence-and-evolution.md](docs/evidence-and-evolution.md) — the
persistence spike confirmed it survives a process restart). What remains for
CP1 is wiring up the whole flow through the frontend form and adding a
notification on confirmation as part of the automated check.

## Submission note

This README and the documentation in `docs/` are updated continuously as
features are added — they reflect the current state of the project, not just
the initial assignment.
..
