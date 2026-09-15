# Specifikace požadavků (SRS) — CarRentalVSB

Seminární práce z předmětu **Softwarové inženýrství** — rezervační systém půjčovny aut.

## 1. Účel a rozsah

Cílem systému je umožnit zákazníkům prohlížet nabídku vozového parku půjčovny a
rezervovat si vozidlo na zvolený termín, a správci půjčovny spravovat vozový
park a přehled rezervací.

Systém se vyvíjí iterativně (viz [roadmap.md](roadmap.md)) — tento dokument
popisuje **cílový rozsah** celého systému. U každého požadavku je uveden
stav implementace.

Stavy: `MVP` (hotovo), `Plánováno` (bude doplněno v dalších iteracích).

## 2. Aktéři

| Aktér | Popis |
|---|---|
| Zákazník | Neregistrovaný nebo registrovaný uživatel, který si chce rezervovat auto. |
| Správce (Admin) | Pracovník půjčovny, spravuje vozový park a rezervace. |
| Systém | Automatizované kontroly (např. dostupnost vozu v termínu). |

## 3. Funkční požadavky

| ID | Požadavek | Aktér | Stav |
|---|---|---|---|
| F1 | Zákazník si může zobrazit seznam dostupných aut (značka, model, rok, cena/den). | Zákazník | MVP |
| F2 | Zákazník si může vytvořit rezervaci vybraného auta na zvolený termín (od–do); rezervace vzniká ve stavu `DRAFT`. | Zákazník | MVP |
| F3 | Systém při vytváření a potvrzování rezervace ověří, že se termín nepřekrývá s jinou **potvrzenou** (`CONFIRMED`) rezervací téhož auta. | Systém | MVP |
| F4 | Zákazník zadává při rezervaci jméno a e-mail; systém podle e-mailu najde nebo založí `User`. | Zákazník | MVP |
| F5 | Registrace a přihlášení zákazníka (účet, historie rezervací). | Zákazník | Plánováno |
| F6 | Zákazník si může svou rezervaci zobrazit a zrušit. | Zákazník | Plánováno (backend `cancel` hotov, výpis „mých" rezervací čeká na F5) |
| F7 | Správce se může přihlásit do administrace. | Admin | Plánováno |
| F8 | Správce může přidat, upravit a odebrat auto z vozového parku. | Admin | Plánováno |
| F9 | Správce vidí přehled všech rezervací a může rezervaci zrušit/potvrdit. | Admin | Plánováno |
| F10 | Systém umožňuje filtrování aut podle kategorie, ceny a dostupnosti v termínu. | Zákazník | Plánováno |
| F11 | Systém podporuje více poboček půjčovny (vyzvednutí/vrácení). | Zákazník | Plánováno |
| F12 | Systém odešle zákazníkovi notifikaci o potvrzení rezervace přes Notification Service. | Systém | MVP (stub) |
| F13 | Systém umožní (mock) platbu za rezervaci. | Zákazník | Plánováno |
| F14 | Zákazník může potvrdit svou rezervaci (`DRAFT → CONFIRMED`); systém před potvrzením znovu ověří dostupnost. | Zákazník | MVP |
| F15 | Zákazník může zrušit svou rezervaci (`→ CANCELLED`); potvrzenou rezervaci lze zrušit jen před začátkem termínu (domain-specific rule). | Zákazník | MVP |
| F16 | Zákazník si může ověřit dostupnost auta v konkrétním termínu bez vytváření rezervace. | Zákazník | MVP |

## 4. Nefunkční požadavky

| ID | Požadavek | Stav |
|---|---|---|
| N1 | Backend poskytuje REST API s automaticky generovanou OpenAPI/Swagger dokumentací. | MVP |
| N2 | Aplikace je rozdělena na samostatný backend (API) a frontend (SPA), komunikujících přes HTTP/JSON. | MVP |
| N3 | Backend je pokryt automatizovanými testy (unit/integrační) se spouštěním přes `pytest`. | MVP |
| N4 | Kód je verzován v Gitu, vývoj probíhá v samostatných větvích s pull requesty. | MVP |
| N5 | Systém validuje vstupní data (typy, povinná pole, formát e-mailu, konzistence termínu od/do). | MVP |
| N6 | Odezva API na běžné požadavky (čtení seznamu aut) do 300 ms na lokálním prostředí. | Plánováno |
| N7 | Hesla uživatelů (po zavedení autentizace) jsou ukládána hashovaná (např. bcrypt), nikdy v čitelné podobě. | Plánováno |
| N8 | Aplikace je responzivní a použitelná na mobilních zařízeních. | Plánováno |
| N9 | Nasazení pomocí kontejnerů (Docker) pro snadné spuštění na jiném stroji. | Plánováno |

## 5. Omezení a předpoklady

- Cílová platforma: moderní webový prohlížeč (desktop i mobil).
- Backend: Python / FastAPI, databáze SQLite pro vývoj (možnost přechodu na PostgreSQL v produkci).
- Frontend: React + TypeScript (Vite).
- Projekt vzniká v rámci výuky — důraz je kladen na dodržení procesu SW inženýrství
  (požadavky → návrh → implementace → testování → dokumentace), nikoliv na produkční
  škálovatelnost.

## 6. Glosář

| Pojem | Význam |
|---|---|
| Rezervace | Závazek zákazníka vypůjčit si konkrétní auto v konkrétním termínu od–do. |
| Dostupnost | Auto je dostupné v termínu, pokud se termín nepřekrývá s jinou existující rezervací. |
| Vozový park | Množina všech aut evidovaných v systému. |
