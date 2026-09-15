# Project Frame

## Reservation domain

Rezervační systém půjčovny aut (car rental). Rezervovaným resource je
konkrétní **auto** ve vozovém parku (identifikováno mj. SPZ).

## Purpose

Systém slouží zákazníkům půjčovny, kteří si chtějí online zkontrolovat
dostupnost auta a vytvořit/potvrdit/zrušit rezervaci na konkrétní termín, a
provozovateli půjčovny, který spravuje vozový park a přehled rezervací.

## Users / Stakeholders

- **Zákazník** — prohlíží vozový park, vytváří, potvrzuje a ruší své rezervace.
- **Správce půjčovny (Admin)** — spravuje vozový park a dohlíží na rezervace (plánováno v dalších iteracích).
- **Notification Service** (externí systém) — informuje zákazníka o potvrzení rezervace.

## Core concepts

- **Reservation** — vazba mezi Resource, User a časovým slotem, se stavem.
- **Resource** (Car) — konkrétní auto ve vozovém parku (značka, model, rok, SPZ, cena/den).
- **User** — osoba, která rezervaci vytváří (jméno, e-mail).

## Core operations

- Create reservation
- Confirm / approve reservation
- Cancel reservation
- Check availability

Implementováno jako REST API:

| Operace | Endpoint |
|---|---|
| Create reservation | `POST /reservations/` |
| Confirm reservation | `POST /reservations/{id}/confirm` |
| Cancel reservation | `POST /reservations/{id}/cancel` |
| Check availability | `GET /cars/{car_id}/availability?start_date=...&end_date=...` |

## Persistent state

**Car (Resource):** id, brand, model, year, license_plate, daily_price.

**User:** id, name, email.

**Reservation:** id, car_id (FK → Car), user_id (FK → User), status
(DRAFT/CONFIRMED/CANCELLED), start_date, end_date, created_at.

## State-changing operation

`DRAFT → CONFIRMED` přes `POST /reservations/{id}/confirm` (systém při tom
znovu ověří dostupnost auta a odešle notifikaci zákazníkovi přes Notification
Service). Dále `DRAFT → CANCELLED` a `CONFIRMED → CANCELLED` přes
`POST /reservations/{id}/cancel`.

## Common business rule

Confirmed reservations for the same resource must not overlap.

Vynuceno v `crud.is_car_available`: kontroluje se pouze proti rezervacím ve
stavu `CONFIRMED` daného auta. Kontrola běží jak při `create` (nelze vytvořit
rezervaci na slot, který už je potvrzený jinou rezervací), tak při `confirm`
(řeší souběh dvou DRAFT rezervací na stejný slot — potvrdit lze jen jednu).

## Domain-specific business rule

**Potvrzenou (CONFIRMED) rezervaci lze zrušit pouze před začátkem termínu
výpůjčky (`start_date` musí být v budoucnosti).** Jakmile výpůjčka podle
`start_date` již začala, zákazník ji přes systém zrušit nemůže — musí se to
řešit provozně (fyzické vrácení/reklamace), ne automatickým zrušením
rezervace, aby nedocházelo k tomu, že „zmizí“ záznam o autě, které je fakticky
mimo půjčovnu.

Implementováno v `crud.cancel_reservation`, otestováno v
`test_cannot_cancel_confirmed_reservation_after_start_date`.

## External / system boundary

**Notification Service** — při potvrzení rezervace (`confirm`) systém zavolá
`NotificationService.send_confirmation(reservation, user)`
(`backend/app/notification.py`). Pro vývoj je zapojena `LoggingNotificationService`
(simuluje úspěšné odeslání a zaloguje ho); v produkci by šlo o reálnou
e-mailovou/SMS bránu. Rozhraní je navrženo tak, aby šlo implementaci vyměnit
beze změny domain kódu — viz [architecture-and-decisions.md](architecture-and-decisions.md).

## Assumption

Předpokládáme, že v této fázi stačí identifikovat zákazníka jménem a
e-mailem bez přihlašování (autentizace) — systém si podle e-mailu
uživatele sám najde nebo založí (`get_or_create_user`). Tento předpoklad
padne, jakmile přibude registrace/přihlášení (F5/F7 v `docs/pozadavky.md`).

## Unknown

Nevíme zatím, jak přesně bude vypadat reálná integrace s Notification
Service (jaký provider, synchronně vs. asynchronně/frontou, jak řešit jeho
výpadek) — to je záměrně otevřené jako budoucí engineering spike (varianta
B — Boundary failure).

---

## Selected future pressure

**Category:** Q — Quality / Scale

**Concrete pressure:** 10× více souběžných rezervací (např. akční nabídka
nebo více poboček najednou generuje výrazně vyšší provoz na `POST
/reservations/` a `POST /reservations/{id}/confirm` ve stejný čas na stejná
auta).

**Why it is relevant to our reservation system:** Kontrola dostupnosti
(`is_car_available`) a přechod DRAFT → CONFIRMED aktuálně běží jako
read-then-write nad SQLite bez explicitního zamykání řádku ani transakční
izolace nastavené na úrovni aplikace. Při 10× vyšší souběžnosti hrozí race
condition — dvě potvrzení téhož slotu projdou téměř současně a poruší
`common business rule` (dvě CONFIRMED rezervace se překryjí). Tato pressure
zatím **není** v C01 řešena implementačně, jen zaznamenaná jako známé riziko
pro budoucí iteraci (bude vyžadovat buď databázový unique/exclusion
constraint, nebo transakci se `SELECT ... FOR UPDATE` po přechodu na
PostgreSQL).
