# Use Cases

## Diagram (target state of the system)

![Use case diagram](diagrams/use-case.svg)

*Diagram source: [diagrams/use-case.puml](diagrams/use-case.puml) — PlantUML, the image is automatically re-rendered on every source change.*

Status legend: ✅ implemented in MVP, ⏳ planned in later iterations.

## UC1 — Browse car offers ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | — |
| Main flow | 1. The customer opens the app. 2. The system shows the list of all cars with brand, model, year and daily price. |
| Alternative flow | The fleet is empty → the system shows an informational message. |
| Result | The customer sees the car offers. |

## UC2 — Create reservation ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | The chosen car exists (UC1). |
| Main flow | 1. The customer picks a car. 2. Enters name, email and the date range (`POST /reservations/`). 3. The system finds/creates the `User` by email. 4. The system runs UC7 (checks availability against CONFIRMED reservations). 5. If the slot is free, the system creates the reservation in `DRAFT` state. |
| Alternative flow A1 | The date range conflicts with a **confirmed** reservation → the system returns error 409. |
| Alternative flow A2 | `end_date` <= `start_date` → the system returns validation error 422. |
| Result | A new reservation exists in the database in `DRAFT` state, linked to the given car, user and date range. |

### Activity diagram — Make Reservation

![Activity diagram — Make Reservation](diagrams/activity-make-reservation.svg)

*Diagram source: [diagrams/activity-make-reservation.puml](diagrams/activity-make-reservation.puml) — PlantUML, the image is automatically re-rendered on every source change.*

## UC7 — Check car availability ✅

| | |
|---|---|
| Actor | System / Customer (`GET /cars/{id}/availability`) |
| Main flow | The system compares the requested date range against all `CONFIRMED` reservations for that car; if no interval overlaps, the car is available. |

## UC3 — Confirm reservation ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | The reservation exists in `DRAFT` state (UC2). |
| Main flow | 1. The customer confirms the reservation (`POST /reservations/{id}/confirm`). 2. The system re-runs UC7 against the other `CONFIRMED` reservations. 3. If the slot is still free, the state changes to `CONFIRMED` and the system sends a notification (UC9). |
| Alternative flow A1 | The reservation isn't in `DRAFT` state (already confirmed/cancelled) → error 409. |
| Alternative flow A2 | Another reservation for an overlapping date range was confirmed in the meantime → error 409, which upholds the common business rule. |
| Result | The reservation is in `CONFIRMED` state, the customer received a notification. |

## UC9 — Send notification ✅ (internal, part of UC3, boundary)

| | |
|---|---|
| Actor | Notification Service (external boundary) |
| Main flow | After confirming a reservation, the system calls `NotificationService.send_confirmation`; in C01, `LoggingNotificationService` is wired in (simulates success). |

## UC8 — Cancel reservation ✅

| | |
|---|---|
| Actor | Customer |
| Precondition | The reservation exists and isn't `CANCELLED`. |
| Main flow | 1. The customer cancels the reservation (`POST /reservations/{id}/cancel`). 2. The system sets the state to `CANCELLED`. |
| Alternative flow A1 | The reservation is already `CANCELLED` → error 409. |
| Alternative flow A2 (domain-specific rule) | The reservation is `CONFIRMED` and `start_date` has already passed → error 409, an ongoing rental can't be cancelled. |
| Result | The reservation is in `CANCELLED` state, the slot is free again for another confirmation. |

## UC4 — Register / log in ⏳

| | |
|---|---|
| Actors | Customer, Admin |
| Main flow | The user enters an email and password; the system verifies the credentials and issues an access token. |

## UC5 — Manage fleet ⏳

| | |
|---|---|
| Actor | Admin |
| Precondition | The admin is logged in. |
| Main flow | The admin adds, edits or removes cars in the fleet. |

## UC6 — Manage reservations ⏳

| | |
|---|---|
| Actor | Admin |
| Precondition | The admin is logged in. |
| Main flow | The admin sees an overview of all reservations, can confirm or cancel them. |
