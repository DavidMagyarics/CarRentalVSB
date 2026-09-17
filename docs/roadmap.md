# Roadmap / iterative development

The project is built in weekly increments. Each item links to the
corresponding requirement in [requirements.md](requirements.md).

## Week 1 — MVP: basic reservation ✅

- [x] Data model `Car`, `Reservation` (F1–F4)
- [x] API: list cars, create reservation with date-overlap check (F3)
- [x] Frontend: car list + reservation form
- [x] Backend tests (unit/integration)
- [x] SWI documentation (SRS, use cases, architecture, domain model, API, test strategy)

## Week 1b — SWI C01: Start the Engineering Project ✅

- [x] `User` entity, reservation states `DRAFT/CONFIRMED/CANCELLED` (F2, F4)
- [x] Confirm/cancel/check availability operations (F14–F16)
- [x] Common business rule only over `CONFIRMED` reservations (F3)
- [x] Domain-specific rule: cannot cancel a confirmed reservation after the rental period has started (F15)
- [x] Notification Service boundary (stub) on confirmation (F12)
- [x] Project Frame, architecture-and-decisions, evidence-and-evolution (`docs/`)
- [x] Persistence engineering spike (process restart, data survived)
- [x] CP1 walking skeleton defined in README

## Week 2 — planned (example, adjust to your instructor's assignment)

- [ ] Frontend UI for confirming/cancelling a reservation and checking availability
- [ ] Frontend component tests (Vitest)

## Week 3 — planned

- [ ] Customer registration and login (F5, F7)
- [ ] Link reservations to the logged-in user instead of name/email

## Week 4 — planned

- [ ] Fleet administration (F8) — add/edit/remove a car
- [ ] Reservation administration (F9) — overview, confirm/cancel

## Week 5+ — planned

- [ ] Filtering cars by availability/price/category (F10)
- [ ] Branches (F11)
- [ ] Email reservation confirmation (F12)
- [ ] CI pipeline (GitHub Actions)
- [ ] Dockerization (N9)

> Note: adjust the specific content of each week to your instructor's actual
> assignment / submission deadlines. This file also serves as the basis for
> ongoing progress evaluation in the course.
