// Czech labels for the car values the API stores in English (the whole UI is Czech).
// A value without a label (e.g. a category the admin added) is shown as it is.

const CAR_LABELS: Record<string, string> = {
  Sedan: 'Sedan',
  SUV: 'SUV',
  Hatchback: 'Hatchback',
  Combi: 'Kombi',
  Van: 'Dodávka',
  Manual: 'Manuální',
  Automatic: 'Automatická',
  Petrol: 'Benzín',
  Diesel: 'Nafta',
  Hybrid: 'Hybrid',
  Electric: 'Elektro',
};

export const carLabel = (value: string): string => CAR_LABELS[value] ?? value;
