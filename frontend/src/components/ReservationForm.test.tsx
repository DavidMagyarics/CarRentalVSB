import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import ReservationForm from './ReservationForm'
import type { Car } from '../api'

// This only exercises the synchronous opening-hours validation
// (`isWithinBusinessHours`), which runs without any network call — so the
// dates picked below are deliberately *outside* business hours, which
// means the component's own availability-check effect never fires and
// nothing here needs to mock `../api`.
vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({ token: 'fake-token' }),
}))
vi.mock('./Toast', () => ({
  useToast: () => ({ show: vi.fn() }),
}))

const car: Car = {
  id: 1,
  brand: 'Škoda',
  model: 'Octavia',
  year: 2022,
  license_plate: '1AB2345',
  daily_price: 1000,
  hourly_price: 100,
  category: 'SEDAN',
  transmission: 'AUTOMATIC',
  fuel_type: 'PETROL',
  seats: 5,
  description: null,
  image_url: null,
  branch_id: 1,
  branch: { id: 1, name: 'Ostrava – centrum', address: 'Testovací 1, Ostrava' },
}

function fillDates(start: string, end: string) {
  const [pickup, returnInput] = screen.getAllByLabelText(/Vyzvednutí|Vrácení/)
  fireEvent.change(pickup, { target: { value: start } })
  fireEvent.change(returnInput, { target: { value: end } })
}

describe('ReservationForm — opening-hours validation (N12/F18, client side)', () => {
  it('blocks a pickup date that falls on a weekend', () => {
    render(<ReservationForm car={car} onDone={vi.fn()} onCancel={vi.fn()} />)

    // 2026-11-07 is a Saturday; 2026-11-09 is the following Monday.
    fillDates('2026-11-07T09:00', '2026-11-09T09:00')

    expect(
      screen.getByText(/Vyzvednutí je možné jen v pracovní dny/),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Potvrdit rezervaci/ })).toBeDisabled()
  })

  it('blocks a return time before the opening hour', () => {
    render(<ReservationForm car={car} onDone={vi.fn()} onCancel={vi.fn()} />)

    fillDates('2026-11-09T09:00', '2026-11-10T07:00')

    expect(screen.getByText(/Vrácení je možné jen v pracovní dny/)).toBeInTheDocument()
  })

  it('blocks a return time after the closing hour', () => {
    render(<ReservationForm car={car} onDone={vi.fn()} onCancel={vi.fn()} />)

    fillDates('2026-11-09T09:00', '2026-11-10T20:30')

    expect(screen.getByText(/Vrácení je možné jen v pracovní dny/)).toBeInTheDocument()
  })

  it('shows no opening-hours error for a valid weekday range', () => {
    render(<ReservationForm car={car} onDone={vi.fn()} onCancel={vi.fn()} />)

    fillDates('2026-11-09T09:00', '2026-11-10T18:00')

    expect(
      screen.queryByText(/je možné jen v pracovní dny/),
    ).not.toBeInTheDocument()
  })
})
