# CarRentalVSB

Rezervační systém půjčovny aut — seminární projekt z předmětu **Softwarové
inženýrství** (SWI), VŠB. Zákazník si prohlédne vozový park, vytvoří
rezervaci, potvrdí ji nebo zruší; systém hlídá, aby se potvrzené rezervace na
jednom autě nekřížily.

Projekt se vyvíjí iterativně, týden po týdnu — aktuální rozsah a plán dalších
přírůstků jsou v [docs/roadmap.md](docs/roadmap.md).

## Tým

| Jméno |
|---|
| David Magyarics |
| Filip Fajtl |
| Daniel Holík |
| František Hanák |

Repozitář: [github.com/DavidMagyarics/CarRentalVSB](https://github.com/DavidMagyarics/CarRentalVSB)

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React, TypeScript, Vite
- **Testy:** pytest (backend)

## Struktura repozitáře

```
backend/    FastAPI REST API
frontend/   React SPA
docs/       Dokumentace SI (požadavky, use case, architektura, ...)
```

## Dokumentace

| Dokument | Obsah |
|---|---|
| [docs/intent-and-change.md](docs/intent-and-change.md) | **Project Frame** (SWI C01) + selected future pressure |
| [docs/architecture-and-decisions.md](docs/architecture-and-decisions.md) | Architektura (C4), decision log, boundary, future pressure (SWI C01) |
| [docs/evidence-and-evolution.md](docs/evidence-and-evolution.md) | **C01 Engineering Spike** — evidence a rozhodnutí |
| [docs/pozadavky.md](docs/pozadavky.md) | Specifikace požadavků (SRS) |
| [docs/pripady-uziti.md](docs/pripady-uziti.md) | Use case diagram a specifikace |
| [docs/architektura.md](docs/architektura.md) | Detailní architektura, struktura repa, volba technologií |
| [docs/domenovy-model.md](docs/domenovy-model.md) | ER / doménový model |
| [docs/api-navrh.md](docs/api-navrh.md) | Návrh REST API |
| [docs/testovaci-strategie.md](docs/testovaci-strategie.md) | Testovací strategie |
| [docs/roadmap.md](docs/roadmap.md) | Plán vývoje po týdnech |

## Spuštění backendu

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows (na Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API poběží na `http://localhost:8000`, interaktivní dokumentace na
`http://localhost:8000/docs`. Při prvním spuštění se vytvoří SQLite databáze
`carrental.db` s pár ukázkovými auty.

### Testy

```bash
cd backend
pytest -v
```

## Spuštění frontendu

```bash
cd frontend
npm install
npm run dev
```

Aplikace poběží na `http://localhost:5173` a očekává backend na
`http://localhost:8000` (lze změnit v `.env` podle `.env.example`).

## CP1 walking skeleton

End-to-end cesta, která bude skutečně runnable (frontend → backend → DB →
automatizovaná kontrola) po C03 / před C04:

```
POST /reservations
→ validate      (auto existuje, end_date > start_date, termín není obsazen CONFIRMED rezervací)
→ persist       (Reservation vznikne ve stavu DRAFT, User se najde/založí podle e-mailu)
→ return reservation ID  (+ status, car_id, user_id)
→ automated check  (pytest: GET /reservations/ vrátí danou rezervaci se stejnými daty)
```

Backendová část tohoto toku je v C01 už implementovaná a otestovaná (viz
[docs/evidence-and-evolution.md](docs/evidence-and-evolution.md) — persistence
spike ověřil, že přežije i restart procesu). Do CP1 zbývá propojit celý tok i
přes frontend formulář a přidat notifikaci při potvrzení jako součást
automatizované kontroly.

## Poznámka k odevzdání

Tento README a dokumentace v `docs/` jsou aktualizovány průběžně s tím, jak
přibývají funkce — odrážejí aktuální stav projektu, ne jen počáteční zadání.
