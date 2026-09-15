# Roadmapa / iterativní vývoj

Projekt se buduje po týdenních přírůstcích. U každé položky je odkaz na
odpovídající požadavek v [pozadavky.md](pozadavky.md).

## Týden 1 — MVP: základní rezervace ✅

- [x] Datový model `Car`, `Reservation` (F1–F4)
- [x] API: výpis aut, vytvoření rezervace s kontrolou kolize termínu (F3)
- [x] Frontend: seznam aut + formulář rezervace
- [x] Backend testy (unit/integrační)
- [x] Dokumentace SI (SRS, use case, architektura, doménový model, API, test strategie)

## Týden 1b — SWI C01: Start the Engineering Project ✅

- [x] `User` entita, stavy rezervace `DRAFT/CONFIRMED/CANCELLED` (F2, F4)
- [x] Operace confirm/cancel/check availability (F14–F16)
- [x] Common business rule jen nad `CONFIRMED` rezervacemi (F3)
- [x] Domain-specific rule: nelze zrušit potvrzenou rezervaci po startu termínu (F15)
- [x] Notification Service boundary (stub) při potvrzení (F12)
- [x] Project Frame, architecture-and-decisions, evidence-and-evolution (`docs/`)
- [x] Persistence engineering spike (restart procesu, data přežila)
- [x] CP1 walking skeleton definován v README

## Týden 2 — návrh (příklad, uprav dle zadání cvičícího)

- [ ] Frontend UI pro potvrzení/zrušení rezervace a kontrolu dostupnosti
- [ ] Frontend testy komponent (Vitest)

## Týden 3 — návrh

- [ ] Registrace a přihlášení zákazníka (F5, F7)
- [ ] Navázání rezervací na přihlášeného uživatele místo jméno/e-mail

## Týden 4 — návrh

- [ ] Administrace vozového parku (F8) — přidání/úprava/odebrání auta
- [ ] Administrace rezervací (F9) — přehled, potvrzení/zrušení

## Týden 5+ — návrh

- [ ] Filtrování aut podle dostupnosti/ceny/kategorie (F10)
- [ ] Pobočky (F11)
- [ ] E-mailové potvrzení rezervace (F12)
- [ ] CI pipeline (GitHub Actions)
- [ ] Dockerizace (N9)

> Poznámka: konkrétní obsah jednotlivých týdnů uprav podle skutečného zadání
> cvičení / termínů odevzdání. Tento soubor slouží i jako podklad pro
> průběžné hodnocení postupu v předmětu.
