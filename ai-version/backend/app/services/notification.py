"""NotificationService boundary interface and its two implementations (UC8a).

Which implementation is used is decided once, at startup
(``create_notification_service``): EmailNotificationService when SMTP_HOST is
configured, LoggingNotificationService otherwise.
"""

from __future__ import annotations

import logging
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage
from typing import TYPE_CHECKING

from ..config import Settings

if TYPE_CHECKING:  # pragma: no cover
    from ..models import Reservation, User

logger = logging.getLogger("carrental.notifications")


def _fmt(dt) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")


def compose_confirmation(reservation: "Reservation", user: "User") -> tuple[str, str]:
    """Subject + body: reservation no., dates and total price."""
    car = reservation.car
    subject = f"Potvrzení rezervace č. {reservation.id}"
    body = (
        f"Dobrý den, {user.name},\n\n"
        f"vaše rezervace č. {reservation.id} byla potvrzena.\n\n"
        f"Auto: {car.brand} {car.model} ({car.license_plate})\n"
        f"Vyzvednutí: {_fmt(reservation.start_date)}\n"
        f"Vrácení: {_fmt(reservation.end_date)}\n"
        f"Celková cena: {reservation.total_price:.2f} Kč\n"
        f"Způsob platby: {'hotově' if reservation.payment_method == 'CASH' else 'kartou'}\n\n"
        "Děkujeme, CarRentalVSB"
    )
    return subject, body


class NotificationService(ABC):
    @abstractmethod
    def send_confirmation(self, reservation: "Reservation", user: "User") -> bool: ...


class LoggingNotificationService(NotificationService):
    """Used when SMTP is not configured: the notification is only written to the log."""

    def send_confirmation(self, reservation: "Reservation", user: "User") -> bool:
        subject, _ = compose_confirmation(reservation, user)
        logger.info(
            "Notification (no e-mail sent) to %s: %s, %s - %s, %.2f",
            user.email,
            subject,
            _fmt(reservation.start_date),
            _fmt(reservation.end_date),
            reservation.total_price,
        )
        return True


class EmailNotificationService(NotificationService):
    """Sends a confirmation e-mail over SMTP (port 587 + STARTTLS by default)."""

    def __init__(self, settings: Settings, smtp_factory=smtplib.SMTP):
        self.settings = settings
        self.smtp_factory = smtp_factory

    def send_confirmation(self, reservation: "Reservation", user: "User") -> bool:
        subject, body = compose_confirmation(reservation, user)
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.smtp_from
        message["To"] = user.email
        message.set_content(body)
        try:
            with self.smtp_factory(
                self.settings.smtp_host, self.settings.smtp_port, timeout=10
            ) as smtp:
                if self.settings.smtp_use_tls:
                    smtp.starttls()
                if self.settings.smtp_user:
                    smtp.login(self.settings.smtp_user, self.settings.smtp_password)
                smtp.send_message(message)
        except Exception:  # noqa: BLE001 - a failure is only logged, r stays CONFIRMED
            logger.exception(
                "Sending the confirmation e-mail for reservation %s failed", reservation.id
            )
            return False
        logger.info("Confirmation e-mail sent to %s (reservation %s)", user.email, reservation.id)
        return True


def create_notification_service(settings: Settings) -> NotificationService:
    if settings.smtp_host:
        return EmailNotificationService(settings)
    return LoggingNotificationService()
