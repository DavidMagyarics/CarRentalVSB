"""Domain errors raised by the services; translated to HTTP responses in main.py.

The messages are taken verbatim from the sequence diagrams where the diagrams give one.
"""

from __future__ import annotations


class DomainError(Exception):
    status_code: int = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class Unauthorized(DomainError):
    status_code = 401


class Forbidden(DomainError):
    status_code = 403


class NotFound(DomainError):
    status_code = 404


class Conflict(DomainError):
    status_code = 409


class Unprocessable(DomainError):
    status_code = 422


# --- messages (from the sequence diagrams) ---------------------------------
MSG_INVALID_CREDENTIALS = "Nesprávný e-mail nebo heslo"
MSG_EMAIL_TAKEN = "Tento e-mail je již zaregistrován"
MSG_ADMIN_REQUIRED = "Vyžadována jsou práva administrátora"
MSG_NOT_YOUR_RESERVATION = "Tato rezervace vám nepatří"
MSG_ALREADY_CANCELLED = "Rezervace je již zrušena"
MSG_RENTAL_STARTED = (
    "Potvrzenou rezervaci nelze zrušit poté, co již začal termín výpůjčky"
)
MSG_SLOT_TAKEN_ON_CONFIRM = "Auto je v tomto termínu už jinou rezervací potvrzeno"
MSG_SLOT_TAKEN_ON_CREATE = "Auto je v požadovaném termínu již potvrzenou rezervací obsazeno"
MSG_OPENING_HOURS = (
    "Vyzvednutí i vrácení auta jsou možné jen v pracovní dny (Po–Pá) mezi 8:00 a 20:00"
)
MSG_NO_CARS_MATCH = "Žádná auta neodpovídají zvoleným filtrům."

# --- messages not given by the diagrams (assumptions) ----------------------
MSG_NOT_AUTHENTICATED = "Nejste přihlášen(a)"
MSG_INVALID_TOKEN = "Neplatný nebo expirovaný token"
MSG_RETURN_BEFORE_PICKUP = "Vrácení auta musí být později než jeho vyzvednutí"
MSG_PICKUP_IN_PAST = "Termín vyzvednutí nesmí být v minulosti"
MSG_RESERVATION_NOT_FOUND = "Rezervace nenalezena"
MSG_CAR_NOT_FOUND = "Auto nenalezeno"
MSG_BRANCH_NOT_FOUND = "Pobočka nenalezena"
MSG_PLATE_TAKEN = "Auto s touto SPZ již existuje"


def msg_cannot_confirm(status: str) -> str:
    return f"Rezervaci ve stavu {status} nelze potvrdit"
