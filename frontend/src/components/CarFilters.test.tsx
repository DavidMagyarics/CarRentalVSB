import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import CarFilters, { EMPTY_FILTERS } from './CarFilters'
import type { FiltersState } from './CarFilters'

describe('CarFilters', () => {
  it('does not show a reset button when no filter is active', () => {
    render(<CarFilters filters={EMPTY_FILTERS} onChange={vi.fn()} />)

    expect(screen.queryByText('Zrušit filtry')).not.toBeInTheDocument()
  })

  it('shows a reset button once a filter is set, and clears all filters when clicked', () => {
    const filters: FiltersState = { ...EMPTY_FILTERS, category: 'SUV' }
    const onChange = vi.fn()
    render(<CarFilters filters={filters} onChange={onChange} />)

    const resetButton = screen.getByText('Zrušit filtry')
    fireEvent.click(resetButton)

    expect(onChange).toHaveBeenCalledWith(EMPTY_FILTERS)
  })

  it('calls onChange with the merged filter state when a dropdown changes', () => {
    const onChange = vi.fn()
    render(<CarFilters filters={EMPTY_FILTERS} onChange={onChange} />)

    fireEvent.change(screen.getByDisplayValue('Všechny kategorie'), {
      target: { value: 'SEDAN' },
    })

    expect(onChange).toHaveBeenCalledWith({ ...EMPTY_FILTERS, category: 'SEDAN' })
  })

  it('updates the min-price input without touching other filters', () => {
    const onChange = vi.fn()
    render(<CarFilters filters={EMPTY_FILTERS} onChange={onChange} />)

    fireEvent.change(screen.getByPlaceholderText('Cena od'), { target: { value: '500' } })

    expect(onChange).toHaveBeenCalledWith({ ...EMPTY_FILTERS, minPrice: '500' })
  })
})
