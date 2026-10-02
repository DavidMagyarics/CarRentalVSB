import type { CarCategory, FuelType, PaymentMethod, ReservationStatus, Transmission } from './api'

// The rental lot's opening hours (F18) — single source of truth, since the
// backend enforces the same rule (see backend/app/schemas.py, N12). Used by
// both the reservation form's validation and anywhere the hours are shown
// as text, so they can't drift apart again.
export const OPENING_HOUR = 8
export const CLOSING_HOUR = 20
export const OPENING_HOURS_LABEL = `Po–Pá ${OPENING_HOUR}:00–${CLOSING_HOUR}:00`

export const CATEGORY_LABELS: Record<CarCategory, string> = {
  SEDAN: 'Sedan',
  SUV: 'SUV',
  HATCHBACK: 'Hatchback',
  VAN: 'Van',
  SPORTS: 'Sportovní',
}

export const TRANSMISSION_LABELS: Record<Transmission, string> = {
  MANUAL: 'Manuál',
  AUTOMATIC: 'Automat',
}

export const FUEL_LABELS: Record<FuelType, string> = {
  PETROL: 'Benzín',
  DIESEL: 'Nafta',
  ELECTRIC: 'Elektro',
  HYBRID: 'Hybrid',
}

export const STATUS_LABELS: Record<ReservationStatus, string> = {
  DRAFT: 'Čeká na schválení administrátorem',
  CONFIRMED: 'Potvrzeno',
  CANCELLED: 'Zrušeno',
}

export const PAYMENT_METHOD_LABELS: Record<PaymentMethod, string> = {
  CASH: 'Hotově',
  CARD: 'Kartou',
}
