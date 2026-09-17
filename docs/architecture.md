# System Architecture

## Overview (C4 — Context level)

![C4 Context diagram](diagrams/context-v1.svg)

*Diagram source: [diagrams/context-v1.puml](diagrams/context-v1.puml) — PlantUML, the image is automatically re-rendered on every source change.*

## Containers (C4 — Container level)

![C4 Container diagram](diagrams/container-v1.svg)

*Diagram source: [diagrams/container-v1.puml](diagrams/container-v1.puml).*

## Technology choice rationale

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI (Python) | Typed schemas (Pydantic), automatic OpenAPI/Swagger docs for free, fast development, easy testing via `TestClient`. |
| ORM / DB access | SQLAlchemy 2.x | Standard in the Python ecosystem, easy move from SQLite to PostgreSQL without code changes. |
| Database (dev) | SQLite | Zero configuration, a single `carrental.db` file, ideal for a school project and local development. |
| Frontend | React + TypeScript (Vite) | Component model matches the domain concepts (car list, reservation form), type safety, fast dev server with HMR. |

## Repository structure

```
CarRentalVSB/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point, CORS, data seeding
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── models.py        # ORM models (Car, Reservation)
│   │   ├── schemas.py       # Pydantic schemas (request/response)
│   │   ├── crud.py          # database logic (incl. availability check)
│   │   └── routers/         # API endpoints by domain
│   ├── tests/                # pytest tests (unit/integration)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api.ts            # HTTP client for the backend
│       ├── components/       # CarList, ReservationForm
│       └── App.tsx
└── docs/                      # this (SWI) documentation
```

## Backend layering

The backend is split into three layers, which makes it easier to test and to
extend later (e.g. with authentication or new entities):

1. **Router (API layer)** — accepts HTTP requests, validates input via Pydantic schemas, returns HTTP responses and error codes.
2. **CRUD (domain/data logic)** — holds the rules over the data, e.g. `is_car_available`, testable in isolation.
3. **Model (persistence)** — SQLAlchemy ORM models mapped to database tables.

This structure is deliberately simple given the scope of the MVP; later
iterations (see [roadmap.md](roadmap.md)) will add an authentication/
authorization layer.
