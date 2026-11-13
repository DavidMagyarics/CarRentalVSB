// The only values a car may have - the backend rejects anything else (422).
// Categories are not fixed any more: the admin manages them (GET /categories/).

export const TRANSMISSIONS = ['Manual', 'Automatic'] as const;
export const FUEL_TYPES = ['Petrol', 'Diesel', 'Hybrid', 'Electric'] as const;

export const CAR_OPTIONS = {
  transmission: TRANSMISSIONS,
  fuel_type: FUEL_TYPES,
} as const;
