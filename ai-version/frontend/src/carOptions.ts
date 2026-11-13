// The only values a car may have - the backend rejects anything else (422).

export const CATEGORIES = ['Sedan', 'SUV', 'Hatchback', 'Combi', 'Van'] as const;
export const TRANSMISSIONS = ['Manual', 'Automatic'] as const;
export const FUEL_TYPES = ['Petrol', 'Diesel', 'Hybrid', 'Electric'] as const;

export const CAR_OPTIONS = {
  category: CATEGORIES,
  transmission: TRANSMISSIONS,
  fuel_type: FUEL_TYPES,
} as const;
