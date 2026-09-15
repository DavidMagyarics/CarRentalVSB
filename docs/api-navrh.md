# Návrh API

Backend po spuštění publikuje interaktivní OpenAPI dokumentaci na
`http://localhost:8000/docs` (Swagger UI) a `http://localhost:8000/redoc` —
ty jsou zdrojem pravdy pro přesná schémata. Tento dokument je jejich čitelný
přehled pro účely dokumentace SI.

## Auta

| Metoda | Cesta | Popis | Odpovědi |
|---|---|---|---|
| GET | `/cars/` | Seznam všech aut | 200 |
| GET | `/cars/{car_id}` | Detail jednoho auta | 200, 404 |
| POST | `/cars/` | Založení nového auta | 201, 422 |

### Schéma `Car`

```json
{
  "id": 1,
  "brand": "Škoda",
  "model": "Octavia",
  "year": 2022,
  "license_plate": "1AB2345",
  "daily_price": 890.0
}
```

## Rezervace

| Metoda | Cesta | Popis | Odpovědi |
|---|---|---|---|
| GET | `/reservations/` | Seznam všech rezervací | 200 |
| POST | `/reservations/` | Vytvoření rezervace | 201, 404 (auto neexistuje), 409 (termín obsazen), 422 (neplatná data) |

### Schéma `ReservationCreate` (request)

```json
{
  "car_id": 1,
  "customer_name": "Jan Novák",
  "customer_email": "jan.novak@example.com",
  "start_date": "2026-10-01T00:00:00",
  "end_date": "2026-10-05T00:00:00"
}
```

### Schéma `Reservation` (response)

```json
{
  "id": 1,
  "car_id": 1,
  "customer_name": "Jan Novák",
  "customer_email": "jan.novak@example.com",
  "start_date": "2026-10-01T00:00:00",
  "end_date": "2026-10-05T00:00:00",
  "created_at": "2026-09-15T14:48:01.489531"
}
```

## Chybové odpovědi

Všechny chyby mají tvar `{"detail": "popis chyby"}` (FastAPI konvence),
u validačních chyb (422) `detail` obsahuje pole s popisem chybných vstupů.

## Plánované endpointy (další iterace)

| Metoda | Cesta | Popis |
|---|---|---|
| POST | `/auth/register`, `/auth/login` | Registrace a přihlášení uživatele |
| GET | `/reservations/me` | Rezervace přihlášeného zákazníka |
| DELETE | `/reservations/{id}` | Zrušení rezervace |
| PUT/PATCH | `/cars/{id}` | Úprava auta (admin) |
| DELETE | `/cars/{id}` | Odebrání auta (admin) |
