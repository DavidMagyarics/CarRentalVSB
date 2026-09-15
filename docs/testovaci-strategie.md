# Testovací strategie

## Přístup

Testovací pyramida je zatím soustředěna na backend, kde je nejvíc doménové
logiky (kontrola dostupnosti auta, validace termínu):

```
        ▲  E2E (plánováno)
       ╱ ╲
      ╱   ╲  Integrační testy API (pytest + FastAPI TestClient) — hotovo
     ╱     ╲
    ╱───────╲  Unit testy komponent frontendu (plánováno)
```

## Co je otestováno (MVP)

Umístění: `backend/tests/`.

| Soubor | Co ověřuje |
|---|---|
| `test_cars.py` | Vytvoření auta, výpis seznamu aut, 404 u neexistujícího auta. |
| `test_reservations.py` | Vytvoření rezervace, 404 pro neexistující auto, odmítnutí překrývajícího se termínu (409), přijetí navazujícího (nepřekrývajícího se) termínu, validace `end_date > start_date` (422). |

Testy běží nad izolovanou in-memory SQLite databází (`tests/conftest.py`),
takže se nedotýkají souboru `carrental.db` používaného při běžném provozu
a jsou na sobě nezávislé.

## Jak spustit testy

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pytest -v
```

## Plánované rozšíření

- Unit testy React komponent (Vitest + React Testing Library) pro `CarList` a `ReservationForm`.
- E2E test hlavního scénáře „zákazník si rezervuje auto“ (Playwright).
- CI pipeline (GitHub Actions) spouštějící `pytest` a `npm run build` při každém pull requestu.
- Testy pro autentizaci a autorizaci po jejich zavedení (viz [roadmap.md](roadmap.md)).

## Manuální testování

Před každým odevzdáním iterace je potřeba ověřit hlavní scénář ručně:

1. Spustit backend (`uvicorn app.main:app --reload`) a frontend (`npm run dev`).
2. Otevřít `http://localhost:5173`, zkontrolovat načtení seznamu aut.
3. Vytvořit rezervaci a ověřit potvrzující hlášku.
4. Zkusit vytvořit kolidující rezervaci a ověřit chybovou hlášku.
