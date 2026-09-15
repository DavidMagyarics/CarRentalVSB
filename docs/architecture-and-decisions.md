# Architecture and Decisions

## Přehled (C4 — Context)

```mermaid
flowchart TB
  zakaznik(("Zákazník"))
  admin(("Správce"))
  app["CarRentalVSB\n(reservation system)"]
  notif["Notification Service\n(externí boundary)"]

  zakaznik -- "prohlíží auta, vytváří/potvrzuje/ruší rezervace (HTTPS)" --> app
  admin -- "spravuje vozový park a rezervace (HTTPS)" --> app
  app -- "send_confirmation(reservation, user)" --> notif
```

## Kontejnery (C4 — Container)

```mermaid
flowchart LR
  subgraph Klient["Prohlížeč"]
    spa["Frontend SPA\nReact + TypeScript (Vite)"]
  end

  subgraph Server["Backend server"]
    api["REST API\nPython / FastAPI"]
    notif["NotificationService\n(boundary interface)"]
    db[("Databáze\nSQLite (dev) / PostgreSQL (prod)")]
  end

  spa -- "HTTP/JSON (fetch)" --> api
  api -- "SQLAlchemy ORM" --> db
  api -- "on confirm" --> notif
```

Podrobnější rozpad struktury repozitáře a vrstvení backendu je v
[architektura.md](architektura.md) (vznikl v první iteraci projektu, obsah
zůstává platný). Tento dokument navíc obsahuje log rozhodnutí, popis boundary
a zvolenou future pressure vyžadovanou zadáním C01.

## External / system boundary: Notification Service

Doména na Notification Service závisí přes malé rozhraní
`NotificationService` (`backend/app/notification.py`):

```python
class NotificationService(Protocol):
    def send_confirmation(self, reservation, user) -> bool: ...
```

Pro vývoj je zapojena `LoggingNotificationService`, která odeslání simuluje a
zaloguje. Reálná integrace (e-mail/SMS provider) se zapojí implementací
stejného rozhraní beze změny domain kódu v `crud.py`/routerech. Chování při
selhání této služby (timeout, 5xx, retry) zatím není řešeno — je to
zaznamenané jako `Unknown` v [intent-and-change.md](intent-and-change.md) a
kandidát na budoucí spike varianty B (Boundary failure).

## Decision log

| # | Rozhodnutí | Zdůvodnění |
|---|---|---|
| D1 | Backend: FastAPI + SQLAlchemy + SQLite (dev) | Automatická OpenAPI dokumentace, typová validace přes Pydantic, nulová konfigurace DB pro školní projekt; snadný přechod na PostgreSQL beze změny ORM kódu. |
| D2 | Frontend: React + TypeScript (Vite) | Komponentový model odpovídá doménovým konceptům (seznam aut, formulář rezervace); rychlý dev server. |
| D3 | Reservation má explicitní stav (`DRAFT`/`CONFIRMED`/`CANCELLED`) místo rovnou "hotové" rezervace | Zadání C01 vyžaduje meaningful states a operace confirm/cancel; DRAFT navíc umožňuje zákazníkovi rozmyslet se bez okamžitého zablokování slotu ostatním. |
| D4 | Common overlap rule se vztahuje jen na `CONFIRMED` rezervace, ne na `DRAFT` | Dvě DRAFT rezervace na stejný slot mohou koexistovat (nikdo ještě nic nezávazně nezabral); závaznost vzniká až potvrzením — viz `crud.is_car_available`. |
| D5 | User se zakládá/najde automaticky podle e-mailu při vytvoření rezervace (`get_or_create_user`), bez přihlašování | V C01 ještě neřešíme autentizaci (F5/F7 jsou `Plánováno`); potřebujeme ale reálnou `User` entitu v datovém modelu podle zadání. |
| D6 | Notification Service je boundary implementovaný jako lokální rozhraní + logging stub, ne reálná HTTP integrace | Cílem C01 je mít definovanou a použitou boundary v kódu; reálná integrace a ošetření výpadků je budoucí práce (viz future pressure a Unknown výše). |

## Selected future pressure

Viz [intent-and-change.md](intent-and-change.md#selected-future-pressure) —
**Category: Q (Quality/Scale)**, konkrétně 10× vyšší souběžnost při
potvrzování rezervací a riziko race condition v `is_car_available` /
`confirm_reservation` nad SQLite bez transakčního zamykání. V C01 se
neimplementuje, jen se eviduje jako známé riziko pro budoucí iteraci.
