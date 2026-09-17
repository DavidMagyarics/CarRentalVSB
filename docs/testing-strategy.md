# Testing Strategy

## Approach

The test pyramid is currently focused on the backend, where most of the
domain logic lives (car availability check, date validation):

```
        ▲  E2E (planned)
       ╱ ╲
      ╱   ╲  API integration tests (pytest + FastAPI TestClient) — done
     ╱     ╲
    ╱───────╲  Frontend component unit tests (planned)
```

## What is tested (MVP)

Location: `backend/tests/`.

| File | What it verifies |
|---|---|
| `test_cars.py` | Creating a car, listing cars, 404 for a non-existent car. |
| `test_reservations.py` | Creating a reservation in `DRAFT` state (+ automatic `User` creation), confirm/cancel and their error states (404/409), the common overlap rule (only `CONFIRMED`), the domain-specific rule for cancelling after the rental period has started, `GET /cars/{id}/availability`, validation of `end_date > start_date` (422). Currently 17 tests. |

Tests run against an isolated in-memory SQLite database (`tests/conftest.py`),
so they never touch the `carrental.db` file used in normal operation and are
independent of each other.

## How to run the tests

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pytest -v
```

## Planned extensions

- Unit tests for React components (Vitest + React Testing Library) for `CarList` and `ReservationForm`.
- E2E test for the main "customer books a car" scenario (Playwright).
- CI pipeline (GitHub Actions) running `pytest` and `npm run build` on every pull request.
- Tests for authentication and authorization once they're introduced (see [roadmap.md](roadmap.md)).

## Manual testing

Before submitting each iteration, the main scenario needs to be verified manually:

1. Start the backend (`uvicorn app.main:app --reload`) and the frontend (`npm run dev`).
2. Open `http://localhost:5173`, check that the car list loads.
3. Create a reservation and verify the confirmation message.
4. Try to create a conflicting reservation and verify the error message.
