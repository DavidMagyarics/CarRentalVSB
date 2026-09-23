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

## Week 2 — Frontend interactions ✅

- [x] Frontend UI for confirming/cancelling a reservation and checking availability
- [ ] Frontend component tests (Vitest) — still planned

## Week 3 — Accounts and roles ✅

- [x] Customer registration and login (F5, F7), JWT bearer tokens
- [x] Reservations tied to the logged-in user instead of name/email (F4)
- [x] Confirming a reservation moved to admin-only (domain-specific rule, see `intent-and-change.md`)

## Week 4 — Administration ✅

- [x] Fleet administration (F8) — add/edit/remove a car
- [x] Reservation administration (F9) — overview, confirm/cancel any reservation

## Week 5 — Full system rebuild ✅

- [x] Filtering cars by category/transmission/fuel/price (F10)
- [x] Hourly + daily pricing with a capped-remainder formula (F17)
- [x] Mock payment method (Cash/Card) at booking time (F13)
- [x] Opening-hours rule (Mon–Fri 08:00–20:00) for pickup/return (F18)
- [x] Real car photos (Wikimedia Commons, self-hosted) with an SVG-illustration fallback
- [x] Support contact widget (F19)
- [x] Optional real e-mail notifications via SMTP env vars, same boundary interface (F12)
- [x] Full black/orange visual redesign
- [x] Complete use case diagram + one activity diagram per use case

## Week 6+ — planned

- [ ] Branches (F11)
- [ ] Real payment provider integration, replacing the mock `payment_method` flag
- [ ] Server-side opening-hours validation once the app tracks customer timezone (N12)
- [ ] CI pipeline (GitHub Actions) running `pytest` and `npm run build` on every pull request
- [ ] Dockerization (N9)
- [ ] Frontend component tests (Vitest) and an E2E test (Playwright)

> Note: adjust the specific content of each week to your instructor's actual
> assignment / submission deadlines. This file also serves as the basis for
> ongoing progress evaluation in the course.
