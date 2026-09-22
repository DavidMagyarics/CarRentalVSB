import type { CarCategory, FuelType, Transmission } from '../api'
import { CATEGORY_LABELS, FUEL_LABELS, TRANSMISSION_LABELS } from '../constants'

export interface FiltersState {
  category: CarCategory | ''
  transmission: Transmission | ''
  fuelType: FuelType | ''
  minPrice: string
  maxPrice: string
}

export const EMPTY_FILTERS: FiltersState = {
  category: '',
  transmission: '',
  fuelType: '',
  minPrice: '',
  maxPrice: '',
}

interface Props {
  filters: FiltersState
  onChange: (filters: FiltersState) => void
}

export default function CarFilters({ filters, onChange }: Props) {
  function set<K extends keyof FiltersState>(key: K, value: FiltersState[K]) {
    onChange({ ...filters, [key]: value })
  }

  const hasActiveFilters =
    filters.category ||
    filters.transmission ||
    filters.fuelType ||
    filters.minPrice ||
    filters.maxPrice

  return (
    <div className="filters">
      <select
        value={filters.category}
        onChange={(e) => set('category', e.target.value as FiltersState['category'])}
      >
        <option value="">Všechny kategorie</option>
        {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>

      <select
        value={filters.transmission}
        onChange={(e) => set('transmission', e.target.value as FiltersState['transmission'])}
      >
        <option value="">Převodovka</option>
        {Object.entries(TRANSMISSION_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>

      <select
        value={filters.fuelType}
        onChange={(e) => set('fuelType', e.target.value as FiltersState['fuelType'])}
      >
        <option value="">Palivo</option>
        {Object.entries(FUEL_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>

      <input
        type="number"
        placeholder="Cena od"
        min={0}
        value={filters.minPrice}
        onChange={(e) => set('minPrice', e.target.value)}
      />
      <input
        type="number"
        placeholder="Cena do"
        min={0}
        value={filters.maxPrice}
        onChange={(e) => set('maxPrice', e.target.value)}
      />

      {hasActiveFilters && (
        <button type="button" className="filters-reset" onClick={() => onChange(EMPTY_FILTERS)}>
          Zrušit filtry
        </button>
      )}
    </div>
  )
}
