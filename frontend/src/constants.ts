import type { CarCategory, FuelType, ReservationStatus, Transmission } from './api'

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
  DRAFT: 'Čeká na potvrzení',
  CONFIRMED: 'Potvrzeno',
  CANCELLED: 'Zrušeno',
}
