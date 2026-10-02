import type { Branch, CarCategory, FuelType, Transmission } from '../api'
import { CATEGORY_LABELS, FUEL_LABELS, TRANSMISSION_LABELS } from '../constants'

export interface FiltersState {
  category: CarCategory | ''
  transmission: Transmission | ''
  fuelType: FuelType | ''
  minPrice: string
  maxPrice: string
  branchId: string
}

export const EMPTY_FILTERS: FiltersState = {
  category: '',
  transmission: '',
  fuelType: '',
  minPrice: '',
  maxPrice: '',
  branchId: '',
}

interface Props {
  filters: FiltersState
  onChange: (filters: FiltersState) => void
  branches?: Branch[]
}

export default function CarFilters({ filters, onChange, branches = [] }: Props) {
  function set<K extends keyof FiltersState>(key: K, value: FiltersState[K]) {
    onChange({ ...filters, [key]: value })
  }

  const hasActiveFilters =
    filters.category ||
    filters.transmission ||
    filters.fuelType ||
    filters.minPrice ||
    filters.maxPrice ||
    filters.branchId

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

      {branches.length > 0 && (
        <select value={filters.branchId} onChange={(e) => set('branchId', e.target.value)}>
          <option value="">Všechny pobočky</option>
          {branches.map((branch) => (
            <option key={branch.id} value={branch.id}>
              {branch.name}
            </option>
          ))}
        </select>
      )}

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
