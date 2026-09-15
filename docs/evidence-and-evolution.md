# C01 Engineering Spike

**Zvolená varianta:** A — Persistence

## Question / unknown

Uloží se doménová data (Car, User, Reservation včetně jejich stavu
DRAFT/CONFIRMED/CANCELLED a vzájemných vazeb) skutečně trvale do databáze
tak, aby přežila restart backendového procesu — a ne jen v paměti běžícího
serveru?

## What we did

1. Rozšířili jsme datový model o entitu `User` a `ReservationStatus`
   (`backend/app/models.py`) a doplnili operace `confirm`/`cancel`/
   `check availability` (`backend/app/crud.py`, `backend/app/routers/`).
2. Smazali jsme soubor databáze (`carrental.db`) pro čistý start.
3. Spustili jsme backend jako proces 1 (`uvicorn app.main:app --port 8010`).
4. Přes `curl` jsme vytvořili rezervaci (`POST /reservations/`) a potvrdili
   ji (`POST /reservations/1/confirm`).
5. Proces 1 jsme tvrdě ukončili (`Stop-Process`).
6. Spustili jsme **nový, nezávislý proces** (proces 2,
   `uvicorn app.main:app --port 8011`) nad stejným souborem `carrental.db`.
7. Přes `curl` jsme na procesu 2 zavolali `GET /reservations/` a
   `GET /users/` — bez jakéhokoliv nového zápisu.
8. Zopakovali jsme celou automatizovanou testovací sadu (`pytest`).

Přesné příkazy a výstupy (zkráceno, plné znění v historii repa / terminálu
při review):

```
$ curl -X POST http://localhost:8010/reservations/ -d '{...car_id:1, spike@example.com, 2027-05-01..2027-05-05}'
{"id":1,"car_id":1,"user_id":1,"status":"DRAFT", ...}

$ curl -X POST http://localhost:8010/reservations/1/confirm
{"id":1,"car_id":1,"user_id":1,"status":"CONFIRMED", ...}

# proces 1 ukončen, proces 2 nastartován nad stejným carrental.db

$ curl http://localhost:8011/reservations/
[{"id":1,"car_id":1,"user_id":1,"status":"CONFIRMED", ...}]

$ curl http://localhost:8011/users/
[{"id":1,"name":"Spike Tester","email":"spike@example.com"}]

$ pytest -q
17 passed
```

## Observed result

Rezervace vytvořená a potvrzená v procesu 1 byla po jeho tvrdém ukončení
čitelná v procesu 2 (jiný proces, jiný port, žádné sdílení paměti) — včetně
správného stavu `CONFIRMED` a navázaného `User` záznamu. Data tedy skutečně
persistují v `carrental.db`, nejsou jen v paměti běžícího serveru. Celá
sada 17 automatizovaných testů (`pytest`) prochází nad touto podobou domény.

## Decision / what changes because of the result

- Zůstáváme u SQLAlchemy + SQLite pro vývoj a školní účely — persistence
  funguje spolehlivě a jednoduše, není důvod ji teď měnit.
- Pro CP1 walking skeleton (viz README) budeme stavět na stejném
  `POST /reservations/` toku, protože je ověřeně funkční end-to-end včetně
  perzistence.
- Riziko souběhu při vyšší zátěži (viz `Selected future pressure` v
  `intent-and-change.md`) SQLite/aplikační zámek zatím neřeší — je to
  vědomě odložené, ne přehlédnuté: až přejdeme na PostgreSQL, doplníme
  transakční zamykání nebo databázový constraint proti překryvu.
- Boundary vůči Notification Service (viz `architecture-and-decisions.md`)
  je zapojen jako stub; jeho reálné selhání (timeout/5xx) je kandidát na
  příští spike (varianta B).
