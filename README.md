# CarRentalVSB

Rezervační systém půjčovny aut — seminární projekt z předmětu **Softwarové
inženýrství**. Zákazník si prohlédne vozový park a rezervuje auto na zvolený
termín; systém hlídá, aby se termíny na jednom autě nekřížily.

Projekt se vyvíjí iterativně, týden po týdnu — aktuální rozsah a plán dalších
přírůstků jsou v [docs/roadmap.md](docs/roadmap.md).

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
| [docs/pozadavky.md](docs/pozadavky.md) | Specifikace požadavků (SRS) |
| [docs/pripady-uziti.md](docs/pripady-uziti.md) | Use case diagram a specifikace |
| [docs/architektura.md](docs/architektura.md) | Architektura (C4), volba technologií |
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

## Poznámka k odevzdání

Tento README a dokumentace v `docs/` jsou aktualizovány průběžně s tím, jak
přibývají funkce — odrážejí aktuální stav projektu, ne jen počáteční zadání.
