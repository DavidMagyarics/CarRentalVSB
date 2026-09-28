# Use Cases

## Diagram (current state of the system)

![Use case diagram](diagrams/use-case.svg)

*Diagram source: [diagrams/use-case.puml](diagrams/use-case.puml) — PlantUML, the image is automatically re-rendered on every source change.*

All use cases below are implemented (✅). Each one that has a meaningfully
independent flow also has its own activity diagram, following the same
structure: one start, one end, and side-by-side swimlanes for every actor
involved. `<<include>>` use cases (Check availability, Send notification)
don't get a separate activity diagram — their steps are shown inline inside
the activity diagram of the use case that includes them (UC4 and UC8).

## Additional diagrams

To document the timing of the availability re-check and the notification call
(a possible race condition), the repository also includes a sequence diagram
for the "Confirm reservation" flow (UC8):
[diagrams/sequence-confirm-reservation.puml](diagrams/sequence-confirm-reservation.puml)

![Sequence diagram — Confirm reservation](diagrams/sequence_confirm_reservation.svg)

## UC1 — Register ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | — |
| Main flow | 1. The customer opens the account modal and picks "Create account". 2. Enters name, e-mail and password (`POST /auth/register`). 3. The system hashes the password (bcrypt), creates the `User` (role `CUSTOMER`) and issues a JWT access token. |
| Alternative flow A1 | The e-mail is already registered → error 409. |
| Result | A new `User` exists; the customer is logged in. |

### Activity diagram — Register

![Activity diagram — Register](diagrams/activity-register.svg)

*Diagram source: [diagrams/activity-register.puml](diagrams/activity-register.puml).*

## UC2 — Log in ✅

| | |
|---|---|
| Actors | Customer, Admin |
| Precondition | The user already has an account (UC1, or seeded — e.g. the demo admin). |
| Main flow | 1. The user enters e-mail and password (`POST /auth/login`). 2. The system verifies the password hash and issues a JWT access token. |
| Alternative flow A1 | Wrong e-mail or password → error 401. |
| Result | The user is logged in; the frontend stores the token and shows role-appropriate tabs (Admin sees the administration tabs). |

### Activity diagram — Log in

![Activity diagram — Log in](diagrams/activity-login.svg)

*Diagram source: [diagrams/activity-login.puml](diagrams/activity-login.puml).*

## UC3 — Browse & filter cars ✅

| | |
|---|---|
| Actor | Customer (no login required) |
| Precondition | — |
| Main flow | 1. The customer opens the app. 2. The system lists all cars (`GET /cars/`). 3. The customer optionally sets filters (category, transmission, fuel type, price range); the system re-queries and returns the matching cars. |
| Alternative flow | The fleet (or the filtered result) is empty → the system shows an informational message. |
| Result | The customer sees a grid of cars matching the current filters, each with a photo (or category illustration), specs, and both the hourly and daily price. |

### Activity diagram — Browse & filter cars

![Activity diagram — Browse & filter cars](diagrams/activity-browse-cars.svg)

*Diagram source: [diagrams/activity-browse-cars.puml](diagrams/activity-browse-cars.puml).*

## UC4 — Create reservation ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | The customer is logged in (UC2) and the chosen car exists (UC3). |
| Main flow | 1. The customer picks a car and opens the booking form. 2. Enters pickup and return date & time. 3. The system runs UC4a (checks availability against `CONFIRMED` reservations). 4. The customer chooses a payment method (Cash, or Card with a mock card-details step that never leaves the browser). 5. On submit, the system computes `total_price` (daily rate per full 24h block, remaining hours at the hourly rate capped at one more day) and creates the reservation in `DRAFT` state with the chosen `payment_method`. |
| Alternative flow A1 | Pickup or return falls outside opening hours (Mon–Fri, 08:00–20:00) → blocked client-side before submission is even possible. |
| Alternative flow A2 | The date range conflicts with a **confirmed** reservation → the system returns error 409. |
| Alternative flow A3 | `end_date` <= `start_date` → the system returns validation error 422. |
| Result | A new reservation exists in `DRAFT` state, linked to the car, the logged-in customer, the chosen dates, the computed price and the payment method — awaiting UC8 (admin approval). |

### Activity diagram — Create reservation

![Activity diagram — Create reservation](diagrams/activity-make-reservation.svg)

*Diagram source: [diagrams/activity-make-reservation.puml](diagrams/activity-make-reservation.puml).*

## UC4a — Check availability ✅ (include, part of UC4 and UC8)

| | |
|---|---|
| Actor | System |
| Main flow | The system compares the requested date range against all `CONFIRMED` reservations for that car; if no interval overlaps, the car is available. Enforced in `crud.is_car_available`. |

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

### Activity diagram — Cancel reservation

![Activity diagram — Cancel reservation](diagrams/activity-cancel-reservation.svg)

*Diagram source: [diagrams/activity-cancel-reservation.puml](diagrams/activity-cancel-reservation.puml).*

## UC6 — View my reservations ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | The customer is logged in. |
| Main flow | 1. The customer opens "My reservations" (`GET /reservations/me`). 2. The system returns only that customer's reservations. 3. The customer sees each one with a car thumbnail, dates, price, payment method and status. |
| Result | The customer has an overview of their own reservations and can cancel any of them (UC5). |

### Activity diagram — View my reservations

![Activity diagram — View my reservations](diagrams/activity-view-my-reservations.svg)

*Diagram source: [diagrams/activity-view-my-reservations.puml](diagrams/activity-view-my-reservations.puml).*

## UC7 — Contact support ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | — |
| Main flow | 1. The customer clicks the floating support button (visible on every page). 2. The system shows a panel with a dummy phone number, e-mail and office hours. 3. Clicking either opens the device's phone/mail app. |
| Result | The customer has a way to reach support, purely client-side (no backend call). |

### Activity diagram — Contact support

![Activity diagram — Contact support](diagrams/activity-contact-support.svg)

*Diagram source: [diagrams/activity-contact-support.puml](diagrams/activity-contact-support.puml).*

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

### Activity diagram — Confirm reservation

![Activity diagram — Confirm reservation](diagrams/activity-confirm-reservation.svg)

*Diagram source: [diagrams/activity-confirm-reservation.puml](diagrams/activity-confirm-reservation.puml).*

## UC8a — Send notification ✅ (include, part of UC8, external boundary)

| | |
|---|---|
| Actor | Notification Service (external boundary) |
| Main flow | After confirming a reservation, the system calls `NotificationService.send_confirmation`. By default `LoggingNotificationService` logs it; if SMTP environment variables are set, `EmailNotificationService` sends a real e-mail instead — same interface, no domain code changes. |

## UC9 — Manage fleet ✅ (admin-only)

| | |
|---|---|
| Actor | Admin |
| Precondition | The admin is logged in. |
| Main flow | The admin adds (`POST /cars/`), edits (`PUT /cars/{id}`) or removes (`DELETE /cars/{id}`) a car in the fleet, including its category, transmission, fuel type, seats, prices, description and photo URL. |
| Alternative flow A1 | A non-admin calls any of these endpoints → error 403. |
| Result | The fleet list reflects the change immediately for all customers. |

### Activity diagram — Manage fleet

![Activity diagram — Manage fleet](diagrams/activity-manage-fleet.svg)

*Diagram source: [diagrams/activity-manage-fleet.puml](diagrams/activity-manage-fleet.puml).*

## UC10 — View all reservations ✅ (admin-only)

| | |
|---|---|
| Actor | Admin |
| Precondition | The admin is logged in. |
| Main flow | The admin opens "All reservations" (`GET /reservations/`) and sees every reservation from every customer, with contact info, dates, price, payment method and status — the entry point for UC8 (confirm) and UC5 (cancel). |
| Alternative flow A1 | A non-admin calls this endpoint → error 403. |
| Result | The admin has a full overview of demand across the fleet. |

### Activity diagram — View all reservations

![Activity diagram — View all reservations](diagrams/activity-view-all-reservations.svg)

*Diagram source: [diagrams/activity-view-all-reservations.puml](diagrams/activity-view-all-reservations.puml).*
