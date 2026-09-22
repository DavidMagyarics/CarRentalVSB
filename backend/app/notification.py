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
import os
import smtplib
from email.message import EmailMessage
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


class EmailNotificationService:
    """Real implementation of the boundary: sends an actual e-mail over SMTP.

    Configured entirely from environment variables (see backend/.env.example)
    so no credentials ever live in code. Used automatically once SMTP_HOST is
    set — see `_build_notification_service` below.
    """

    def __init__(self) -> None:
        self.host = os.environ["SMTP_HOST"]
        self.port = int(os.environ.get("SMTP_PORT", "587"))
        self.username = os.environ.get("SMTP_USER")
        self.password = os.environ.get("SMTP_PASSWORD")
        self.from_email = os.environ.get("SMTP_FROM", self.username or "")

    def send_confirmation(self, reservation: models.Reservation, user: models.User) -> bool:
        message = EmailMessage()
        message["Subject"] = f"Rezervace #{reservation.id} potvrzena — CarRentalVSB"
        message["From"] = self.from_email
        message["To"] = user.email
        message.set_content(
            f"Dobrý den {user.name},\n\n"
            f"vaše rezervace č. {reservation.id} byla potvrzena.\n"
            f"Termín: {reservation.start_date:%d.%m.%Y %H:%M} "
            f"– {reservation.end_date:%d.%m.%Y %H:%M}\n"
            f"Celková cena: {reservation.total_price:.0f} Kč\n\n"
            "Děkujeme, že využíváte CarRentalVSB.\n"
        )
        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
                smtp.starttls()
                if self.username and self.password:
                    smtp.login(self.username, self.password)
                smtp.send_message(message)
        except Exception:
            logger.exception(
                "Failed to e-mail confirmation for reservation %s to %s",
                reservation.id,
                user.email,
            )
            return False

        logger.info("Confirmation e-mail sent for reservation %s to %s", reservation.id, user.email)
        return True


def _build_notification_service() -> NotificationService:
    if os.environ.get("SMTP_HOST"):
        return EmailNotificationService()
    return LoggingNotificationService()


notification_service: NotificationService = _build_notification_service()
