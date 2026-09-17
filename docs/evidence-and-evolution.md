# C01 Engineering Spike

**Chosen variant:** A — Persistence

## Question / unknown

Is the domain data (Car, User, Reservation including its
DRAFT/CONFIRMED/CANCELLED state and their relationships) actually persisted
to the database so it survives a backend process restart — and not just kept
in the memory of the running server?

## What we did

1. We extended the data model with a `User` entity and `ReservationStatus`
   (`backend/app/models.py`) and added `confirm`/`cancel`/
   `check availability` operations (`backend/app/crud.py`, `backend/app/routers/`).
2. We deleted the database file (`carrental.db`) for a clean start.
3. We started the backend as process 1 (`uvicorn app.main:app --port 8010`).
4. Via `curl` we created a reservation (`POST /reservations/`) and confirmed
   it (`POST /reservations/1/confirm`).
5. We hard-killed process 1 (`Stop-Process`).
6. We started a **new, independent process** (process 2,
   `uvicorn app.main:app --port 8011`) over the same `carrental.db` file.
7. Via `curl` we called `GET /reservations/` and `GET /users/` on process 2 —
   without any new write.
8. We re-ran the whole automated test suite (`pytest`).

Exact commands and output (abridged, full record in the repo/terminal history
at review time):

```
$ curl -X POST http://localhost:8010/reservations/ -d '{...car_id:1, spike@example.com, 2027-05-01..2027-05-05}'
{"id":1,"car_id":1,"user_id":1,"status":"DRAFT", ...}

$ curl -X POST http://localhost:8010/reservations/1/confirm
{"id":1,"car_id":1,"user_id":1,"status":"CONFIRMED", ...}

# process 1 killed, process 2 started over the same carrental.db

$ curl http://localhost:8011/reservations/
[{"id":1,"car_id":1,"user_id":1,"status":"CONFIRMED", ...}]

$ curl http://localhost:8011/users/
[{"id":1,"name":"Spike Tester","email":"spike@example.com"}]

$ pytest -q
17 passed
```

## Observed result

The reservation created and confirmed in process 1 was readable in process 2
after process 1 was hard-killed (a different process, a different port, no
shared memory) — including the correct `CONFIRMED` status and the linked
`User` record. So the data really does persist in `carrental.db`, it isn't
just in the memory of the running server. The full suite of 17 automated
tests (`pytest`) passes against this shape of the domain.

## Decision / what changes because of the result

- We're staying with SQLAlchemy + SQLite for development and school purposes
  — persistence works reliably and simply, there's no reason to change it
  now.
- For the CP1 walking skeleton (see README) we'll build on the same
  `POST /reservations/` flow, since it's proven to work end-to-end including
  persistence.
- The risk of concurrency under higher load (see `Selected future pressure`
  in `intent-and-change.md`) is not addressed by SQLite/an application lock
  yet — this is a conscious deferral, not an oversight: once we move to
  PostgreSQL we'll add transactional locking or a database constraint against
  overlap.
- The boundary to the Notification Service (see `architecture-and-decisions.md`)
  is wired in as a stub; its real failure modes (timeout/5xx) are a candidate
  for the next spike (variant B).
