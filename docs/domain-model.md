# Domain / ER Model

## Current state

![ER diagram — current state](diagrams/er-current.svg)

*Diagram source: [diagrams/er-current.puml](diagrams/er-current.puml) — PlantUML, the image is automatically re-rendered on every source change.*

**User accounts:** `User` has a hashed password (bcrypt) and a `role`
(`CUSTOMER` or `ADMIN`). Reservations belong to the logged-in user — there is
no more anonymous name/e-mail booking; see [api-design.md](api-design.md) for
the auth endpoints.

**Car pricing and specs:** `Car` carries both `daily_price` and
`hourly_price` (see the pricing rule below), plus `category`, `transmission`,
`fuel_type`, `seats`, an optional `description` and an optional `image_url`
(falls back to a category illustration in the UI when absent).

**Reservation pricing and payment:** `Reservation` stores a server-computed
`total_price` (locked in at creation time, so it doesn't change if the car's
price changes later) and a `payment_method` (`CASH` or `CARD` — card details
themselves are never stored or transmitted, this is a mock payment step).

**Reservation states:** `DRAFT → CONFIRMED → (terminal)`, `DRAFT → CANCELLED`,
`CONFIRMED → CANCELLED` (only before `start_date`, see the domain-specific
rule in [intent-and-change.md](intent-and-change.md)). `DRAFT → CONFIRMED` is
an **admin-only** transition — see UC8 in [use-cases.md](use-cases.md).

**Consistency rule (common business rule):** for a given `car_id`, the
database must never contain two reservations in `CONFIRMED` state with
overlapping `[start_date, end_date)` intervals. This rule is enforced at the
application level (`crud.is_car_available`), not by a database constraint —
see [testing-strategy.md](testing-strategy.md) and the recorded risk under
`Selected future pressure` in [intent-and-change.md](intent-and-change.md).

**Pricing rule:** `crud.calculate_price` bills full 24h blocks at
`daily_price`; the remaining hours are billed at `hourly_price` but capped at
one more `daily_price`, so a booking close to (or over) a full day is never
worse than booking it by the day. Mirrored client-side in `src/pricing.ts`
for instant feedback while picking dates; the server value is authoritative.

## Target model (after further iterations)

![ER diagram — target model](diagrams/er-target.svg)

*Diagram source: [diagrams/er-target.puml](diagrams/er-target.puml).*

Extensions still ahead: a `BRANCH` entity for multiple pickup/return
locations (F11), a proper `CAR_CATEGORY` table instead of today's fixed enum
(so categories become manageable data, not hardcoded values), and a
`PAYMENT` entity recording a real transaction (provider ID, amount, status,
timestamp) once the mock Cash/Card step is replaced with a real payment
provider.
