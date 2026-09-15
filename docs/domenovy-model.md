# Doménový / ER model

## Aktuální stav (MVP)

```mermaid
erDiagram
  CAR ||--o{ RESERVATION : "je rezervováno v"

  CAR {
    int id PK
    string brand
    string model
    int year
    string license_plate
    float daily_price
  }

  RESERVATION {
    int id PK
    int car_id FK
    string customer_name
    string customer_email
    datetime start_date
    datetime end_date
    datetime created_at
  }
```

**Pravidlo konzistence:** pro dané `car_id` se nesmí v databázi vyskytnout dvě
rezervace s překrývajícím se intervalem `[start_date, end_date)`. Toto pravidlo
je vynucováno na úrovni aplikace (`crud.is_car_available`), ne databázovým
constraintem — viz [testovaci-strategie.md](testovaci-strategie.md).

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
