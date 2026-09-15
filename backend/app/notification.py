"""External/system boundary: Notification Service.

The reservation domain depends on a Notification Service to inform the
customer when their reservation is confirmed. In production this would be a
separate system reached over HTTP/queue (e-mail or SMS provider); for now we
depend only on the small interface below (`NotificationService`), so the real
integration can be swapped in later without touching domain code — see
docs/architecture-and-decisions.md for the boundary discussion and
docs/evidence-and-evolution.md for how this is expected to evolve (spike B).
"""

from __future__ import annotations

import logging
from typing import Protocol

from . import models

logger = logging.getLogger("carrentalvsb.notification")


class NotificationService(Protocol):
    def send_confirmation(self, reservation: models.Reservation, user: models.User) -> bool:
        ...


class LoggingNotificationService:
    """Development stand-in for a real Notification Service.

    Simulates a successful delivery and just logs it, so the rest of the
    domain can depend on the `NotificationService` boundary today without a
    real provider being wired up yet.
    """

    def send_confirmation(self, reservation: models.Reservation, user: models.User) -> bool:
        logger.info(
            "Notification: reservation %s for car %s confirmed for %s <%s>",
            reservation.id,
            reservation.car_id,
            user.name,
            user.email,
        )
        return True


notification_service: NotificationService = LoggingNotificationService()
