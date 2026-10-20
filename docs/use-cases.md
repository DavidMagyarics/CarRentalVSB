# Use Cases

This document is the use case specification for CarRentalVSB: it defines,
for every piece of functionality a Customer or an Admin can use, who
triggers it, under what precondition, what the exact main and alternative
flows are (with the real API endpoint and HTTP status behind each one), and
what the system guarantees once it succeeds. It is the single source of
truth for *what the system does*, independent of how any particular screen
happens to be laid out.

## Use Case Diagram

![Use case diagram](diagrams/use-case.svg)

*Diagram source: [diagrams/use-case.puml](diagrams/use-case.puml) — PlantUML, the image is automatically re-rendered on every source change.*

### What this diagram specifies

The diagram above is the complete functional scope of CarRentalVSB as it is
actually implemented today: **2 actors** and **12 use cases**, covering
everything a customer or an admin can do in the system, from creating an
account to approving a reservation. It is read left to right: an actor
(stick figure) is connected to every use case (oval) it can trigger
directly; a dashed arrow labelled `<<include>>` means one use case always
triggers another as an internal step of its own flow, rather than an actor
triggering it directly.

**Customer** — anyone can browse the fleet and register without an account,
but everything else needs one. A customer can register (UC1), log in (UC2),
browse and filter the fleet (UC3), create (UC4) and cancel (UC5) their own
reservations, see their own reservation history (UC6), and reach support
(UC7).

**Admin** — shares the same login screen and endpoint as customers (UC2);
the account's `role` field is what unlocks the administration tabs on the
frontend, not a separate login. An admin additionally confirms pending
reservations (UC8), manages the fleet (UC9), sees every customer's
reservations (UC10), and — unlike a customer — can cancel *any* reservation
(UC5), not only their own.

Two use cases are never triggered by an actor directly; they only ever run
as a step **inside** another use case, which is exactly what the
`<<include>>` relationship means here:

- **UC4a — Check availability** runs inside UC4, twice (once live while the
  customer is still picking dates, once more right before the reservation
  is actually created), and inside UC8, once more, right before a
  reservation is confirmed.
- **UC8a — Send notification** runs inside UC8, immediately after a
  reservation becomes `CONFIRMED`.

Every use case on this diagram is implemented (✅) — there are no
planned/future use cases in the model. Multiple rental branches (F11) are
not a separate use case: they extend existing ones (a car's branch is shown
and filterable in UC3, and required when managing the fleet in UC9) — see
[requirements.md](requirements.md).

## How the system is documented

The use cases are described in this document; the diagrams that illustrate
them are kept in separate documents, one per kind of diagram:

| Document | What it contains |
|---|---|
| **use-cases.md** (this document) | The use case diagram and, for every use case, a table — actor(s), precondition, the numbered main flow (with the real API endpoint each step calls), every alternative/error flow with its HTTP status code, and the result once the use case succeeds. This is the authoritative description; the diagrams in the other documents are illustrations of it, not additional requirements. |
| [activity-diagrams.md](activity-diagrams.md) | One activity diagram per use case — the same flow as a flowchart. |
| [sequence-diagrams.md](sequence-diagrams.md) | One sequence diagram per use case — the same flow as messages between objects. |
| [class-diagram.md](class-diagram.md) | The class diagram — every class whose objects appear in the sequence diagrams. |
| [state-diagrams.md](state-diagrams.md) | State diagrams of the classes whose behaviour depends on their state. |

## UC1 — Register ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | — |
| Main flow | 1. The customer opens the account modal and picks "Create account". 2. Enters name, e-mail and password (`POST /auth/register`). 3. The system hashes the password (bcrypt), creates the `User` (role `CUSTOMER`) and issues a JWT access token. |
| Alternative flow A1 | The e-mail is already registered → error 409. |
| Result | A new `User` exists; the customer is logged in. |

Diagrams: [activity diagram](activity-diagrams.md#uc1--register) · [sequence diagram](sequence-diagrams.md#uc1--register)

## UC2 — Log in ✅

| | |
|---|---|
| Actors | Customer, Admin |
| Precondition | The user already has an account (UC1, or seeded — e.g. the demo admin). |
| Main flow | 1. The user enters e-mail and password (`POST /auth/login`). 2. The system verifies the password hash and issues a JWT access token. |
| Alternative flow A1 | Wrong e-mail or password → error 401. |
| Result | The user is logged in; the frontend stores the token and shows role-appropriate tabs (Admin sees the administration tabs). |

Diagrams: [activity diagram](activity-diagrams.md#uc2--log-in) · [sequence diagram](sequence-diagrams.md#uc2--log-in)

## UC3 — Browse & filter cars ✅

| | |
|---|---|
| Actor | Customer (no login required) |
| Precondition | — |
| Main flow | 1. The customer opens the app. 2. The system lists all cars (`GET /cars/`). 3. The customer optionally sets filters (category, transmission, fuel type, price range, branch — F11); the system re-queries and returns the matching cars. |
| Alternative flow | The fleet (or the filtered result) is empty → the system shows an informational message. |
| Result | The customer sees a grid of cars matching the current filters, each with a photo (or category illustration), specs, branch, and both the hourly and daily price. |

Diagrams: [activity diagram](activity-diagrams.md#uc3--browse--filter-cars) · [sequence diagram](sequence-diagrams.md#uc3--browse--filter-cars)

## UC4 — Create reservation ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | The customer is logged in (UC2) and the chosen car exists (UC3). |
| Main flow | 1. The customer picks a car and clicks "Reserve" (a logged-out visitor is asked to log in or register first, then the booking form opens). 2. Enters pickup and return date & time. 3. The system runs UC4a while the form is being filled (checks availability against `CONFIRMED` reservations). 4. The customer chooses a payment method (Cash, or Card with a mock card-details step that never leaves the browser). 5. On submit, the system runs UC4a again, computes `total_price` (daily rate per full 24h block, remaining hours at the hourly rate capped at one more day) and creates the reservation in `DRAFT` state with the chosen `payment_method`. |
| Alternative flow A1 | Pickup or return falls outside opening hours (Mon–Fri, 08:00–20:00) → blocked client-side before submission is even possible; the API also rejects it server-side (422) if it's ever submitted anyway. |
| Alternative flow A2 | The date range conflicts with a **confirmed** reservation → the form shows it and submitting is disabled; if the slot gets confirmed between that check and the submit, the system returns error 409. |
| Alternative flow A3 | `end_date` <= `start_date` → blocked in the form; the API returns validation error 422. |
| Result | A new reservation exists in `DRAFT` state, linked to the car, the logged-in customer, the chosen dates, the computed price and the payment method — awaiting UC8 (admin approval). |

Diagrams: [activity diagram](activity-diagrams.md#uc4--create-reservation) · [sequence diagram](sequence-diagrams.md#uc4--create-reservation)

## UC4a — Check availability ✅ (include, part of UC4 and UC8)

| | |
|---|---|
| Actor | System |
| Main flow | The system compares the requested date range against all `CONFIRMED` reservations for that car; if no interval overlaps, the car is available. Enforced in `crud.is_car_available`. |

Diagrams: [activity diagram](activity-diagrams.md#uc4a--check-availability) · [sequence diagram](sequence-diagrams.md#uc4a--check-availability)

## UC5 — Cancel reservation ✅

| | |
|---|---|
| Actors | Customer (own reservations), Admin (any reservation) |
| Precondition | The reservation exists and isn't already `CANCELLED`. |
| Main flow | 1. The user clicks "Cancel" (`POST /reservations/{id}/cancel`). 2. The system sets the state to `CANCELLED`. |
| Alternative flow A1 | The reservation is already `CANCELLED` → error 409. |
| Alternative flow A2 (domain-specific rule) | The reservation is `CONFIRMED` and `start_date` has already passed → error 409, an ongoing rental can't be cancelled. |
| Alternative flow A3 | A customer tries to cancel someone else's reservation → error 403 (owner-or-admin check). |
| Result | The reservation is `CANCELLED`; the slot is free again for another confirmation. |

Diagrams: [activity diagram](activity-diagrams.md#uc5--cancel-reservation) · [sequence diagram](sequence-diagrams.md#uc5--cancel-reservation)

## UC6 — View my reservations ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | The customer is logged in. |
| Main flow | 1. The customer opens "My reservations" (`GET /reservations/me`). 2. The system returns only that customer's reservations. 3. The customer sees each one with a car thumbnail, dates, price, payment method and status. |
| Result | The customer has an overview of their own reservations and can cancel any of them (UC5). |

Diagrams: [activity diagram](activity-diagrams.md#uc6--view-my-reservations) · [sequence diagram](sequence-diagrams.md#uc6--view-my-reservations)

## UC7 — Contact support ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | — |
| Main flow | 1. The customer clicks the floating support button (visible on every page). 2. The system shows a panel with a dummy phone number, e-mail and office hours. 3. Clicking either opens the device's phone/mail app. |
| Result | The customer has a way to reach support, purely client-side (no backend call). |

Diagrams: [activity diagram](activity-diagrams.md#uc7--contact-support) · [sequence diagram](sequence-diagrams.md#uc7--contact-support)

## UC8 — Confirm reservation ✅ (admin-only)

| | |
|---|---|
| Actor | Admin |
| Precondition | The reservation exists in `DRAFT` state (UC4). The customer **cannot** confirm their own reservation — this is a deliberate domain rule: a request only becomes binding once staff has approved it. |
| Main flow | 1. The admin opens "All reservations" and clicks "Confirm" on a pending one (`POST /reservations/{id}/confirm`). 2. The system re-runs UC4a against the other `CONFIRMED` reservations. 3. If the slot is still free, the state changes to `CONFIRMED` and the system runs UC8a (sends a confirmation notification). |
| Alternative flow A1 | The reservation isn't in `DRAFT` state anymore → error 409. |
| Alternative flow A2 | Another reservation for an overlapping date range was confirmed in the meantime → error 409, which upholds the common business rule. |
| Alternative flow A3 | A non-admin tries to confirm → error 403. |
| Result | The reservation is `CONFIRMED`; the customer has received a notification. |

Diagrams: [activity diagram](activity-diagrams.md#uc8--confirm-reservation) · [sequence diagram](sequence-diagrams.md#uc8--confirm-reservation)

## UC8a — Send notification ✅ (include, part of UC8, external boundary)

| | |
|---|---|
| Actor | Notification Service (external boundary) |
| Main flow | After confirming a reservation, the system calls `NotificationService.send_confirmation`. By default `LoggingNotificationService` logs it; if SMTP environment variables are set, `EmailNotificationService` sends a real e-mail instead — same interface, no domain code changes. If sending the e-mail fails, the error is only logged and the reservation stays `CONFIRMED`. |

Diagrams: [activity diagram](activity-diagrams.md#uc8a--send-notification) · [sequence diagram](sequence-diagrams.md#uc8a--send-notification)

## UC9 — Manage fleet ✅ (admin-only)

| | |
|---|---|
| Actor | Admin |
| Precondition | The admin is logged in. |
| Main flow | The admin adds (`POST /cars/`), edits (`PUT /cars/{id}`) or removes (`DELETE /cars/{id}`) a car in the fleet, including its category, transmission, fuel type, seats, prices, description, photo URL and branch (F11, required — every car belongs to exactly one). Removing a car also deletes all of its reservations. |
| Alternative flow A1 | A non-admin calls any of these endpoints → error 403. |
| Alternative flow A2 | `branch_id` doesn't reference an existing branch → error 404. |
| Result | The fleet list reflects the change immediately for all customers. |

Diagrams: [activity diagram](activity-diagrams.md#uc9--manage-fleet) · [sequence diagram](sequence-diagrams.md#uc9--manage-fleet)

## UC10 — View all reservations ✅ (admin-only)

| | |
|---|---|
| Actor | Admin |
| Precondition | The admin is logged in. |
| Main flow | The admin opens "All reservations" (`GET /reservations/`) and sees every reservation from every customer, with contact info, dates, price, payment method and status — the entry point for UC8 (confirm) and UC5 (cancel). |
| Alternative flow A1 | A non-admin calls this endpoint → error 403. |
| Result | The admin has a full overview of demand across the fleet. |

Diagrams: [activity diagram](activity-diagrams.md#uc10--view-all-reservations) · [sequence diagram](sequence-diagrams.md#uc10--view-all-reservations)
