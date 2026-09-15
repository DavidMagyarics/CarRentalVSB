# Doménový / ER model

## Aktuální stav (C01)

```mermaid
erDiagram
  CAR ||--o{ RESERVATION : "je rezervováno v"
  USER ||--o{ RESERVATION : "vytváří"

  CAR {
    int id PK
    string brand
    string model
    int year
    string license_plate
    float daily_price
  }

  USER {
    int id PK
    string name
    string email
  }

  RESERVATION {
    int id PK
    int car_id FK
    int user_id FK
    string status "DRAFT | CONFIRMED | CANCELLED"
    datetime start_date
    datetime end_date
    datetime created_at
  }
```

**Stavy rezervace:** `DRAFT → CONFIRMED → (terminál)`, `DRAFT → CANCELLED`,
`CONFIRMED → CANCELLED` (jen před `start_date`, viz domain-specific rule v
[intent-and-change.md](intent-and-change.md)).

**Pravidlo konzistence (common business rule):** pro dané `car_id` se nesmí
v databázi vyskytnout dvě rezervace ve stavu `CONFIRMED` s překrývajícím se
intervalem `[start_date, end_date)`. Toto pravidlo je vynucováno na úrovni
aplikace (`crud.is_car_available`), ne databázovým constraintem — viz
[testovaci-strategie.md](testovaci-strategie.md) a zaznamenané riziko pod
`Selected future pressure` v [intent-and-change.md](intent-and-change.md).

`User` se v C01 zakládá automaticky podle e-mailu při vytvoření rezervace
(bez registrace/přihlášení) — viz `Assumption` v
[intent-and-change.md](intent-and-change.md).

## Cílový model (po dalších iteracích)

```mermaid
erDiagram
  USER ||--o{ RESERVATION : "vytváří"
  CAR ||--o{ RESERVATION : "je rezervováno v"
  BRANCH ||--o{ CAR : "patří pod"
  CAR ||--o{ CAR_CATEGORY : "spadá do"

  USER {
    int id PK
    string email
    string password_hash
    string role
  }

  BRANCH {
    int id PK
    string name
    string address
  }

  CAR {
    int id PK
    string brand
    string model
    int year
    string license_plate
    float daily_price
    int branch_id FK
    int category_id FK
  }

  RESERVATION {
    int id PK
    int car_id FK
    int user_id FK
    datetime start_date
    datetime end_date
    string status
    datetime created_at
  }
```

Rozšíření oproti MVP: registrovaní uživatelé (`USER`) nahrazují prosté
`customer_name`/`customer_email`, přibývá pobočka (`BRANCH`), kategorie vozu a
stav rezervace (`status`: čeká / potvrzena / zrušena).
