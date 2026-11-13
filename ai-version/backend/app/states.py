"""State design pattern for Reservation (pattern-state.puml, state-reservation.puml).

``Reservation`` is the *context*; it delegates ``confirm()``, ``cancel()`` and
``blocks_car()`` to its current ``ReservationState``. Every concrete state decides
whether the transition is allowed and, if so, calls ``context.set_state(...)``.

The stored column ``reservation.status`` (DRAFT | CONFIRMED | CANCELLED) is the
persistent form of the state; the state object is rebuilt from it on demand, so
objects loaded from the database behave exactly like freshly created ones.

The guards from the diagrams are passed in by the caller (ReservationService):
* ``car_available`` - result of UC4a for DraftState.confirm()
* ``now``           - current time, used for the "Before pickup" / "Rental started"
                      sub-states of CONFIRMED (they are not stored, they follow
                      from the current time).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from .errors import (
    MSG_ALREADY_CANCELLED,
    MSG_RENTAL_STARTED,
    MSG_SLOT_TAKEN_ON_CONFIRM,
    Conflict,
    msg_cannot_confirm,
)

if TYPE_CHECKING:  # pragma: no cover
    from .models import Reservation


class ReservationStatus:
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

    ALL = (DRAFT, CONFIRMED, CANCELLED)


class ReservationState(ABC):
    """Abstract state. ``status`` is the value persisted in the database."""

    status: str

    def __init__(self, context: "Reservation"):
        self.context = context

    @abstractmethod
    def confirm(self, car_available: bool = True) -> None: ...

    @abstractmethod
    def cancel(self, now: datetime | None = None) -> None: ...

    @classmethod
    @abstractmethod
    def blocks_car(cls) -> bool: ...

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<{type(self).__name__}>"


class DraftState(ReservationState):
    """DRAFT - only a request waiting for the admin's approval."""

    status = ReservationStatus.DRAFT

    def confirm(self, car_available: bool = True) -> None:
        if not car_available:
            # [slot taken by another CONFIRMED reservation] / reject (409)
            raise Conflict(MSG_SLOT_TAKEN_ON_CONFIRM)
        self.context.set_state(ConfirmedState(self.context))

    def cancel(self, now: datetime | None = None) -> None:
        self.context.set_state(CancelledState(self.context))

    @classmethod
    def blocks_car(cls) -> bool:
        return False  # only a request


class ConfirmedState(ReservationState):
    """CONFIRMED - blocks the car for [start_date, end_date)."""

    status = ReservationStatus.CONFIRMED

    def confirm(self, car_available: bool = True) -> None:
        raise Conflict(msg_cannot_confirm(self.status))  # already confirmed

    def cancel(self, now: datetime | None = None) -> None:
        if self.rental_started(now):
            raise Conflict(MSG_RENTAL_STARTED)
        self.context.set_state(CancelledState(self.context))

    def rental_started(self, now: datetime | None = None) -> bool:
        """Sub-state of CONFIRMED: "Before pickup" (False) vs "Rental started" (True)."""
        now = now or datetime.now()
        return now >= self.context.start_date

    @classmethod
    def blocks_car(cls) -> bool:
        return True


class CancelledState(ReservationState):
    """CANCELLED - final state, the time slot is free again."""

    status = ReservationStatus.CANCELLED

    def confirm(self, car_available: bool = True) -> None:
        raise Conflict(msg_cannot_confirm(self.status))

    def cancel(self, now: datetime | None = None) -> None:
        raise Conflict(MSG_ALREADY_CANCELLED)

    @classmethod
    def blocks_car(cls) -> bool:
        return False  # slot is free again


STATE_BY_STATUS: dict[str, type[ReservationState]] = {
    cls.status: cls for cls in (DraftState, ConfirmedState, CancelledState)
}

# Statuses whose state blocks the car - used by the single availability query (UC4a).
BLOCKING_STATUSES: tuple[str, ...] = tuple(
    status for status, cls in STATE_BY_STATUS.items() if cls.blocks_car()
)


def state_for(context: "Reservation") -> ReservationState:
    return STATE_BY_STATUS[context.status](context)
