import { describe, expect, it } from 'vitest'
import { calculatePrice, formatDuration } from './pricing'

// Mirrors backend/tests/test_reservations.py's price-calculation tests —
// the frontend estimate shown while picking dates must match what the
// server will actually charge (crud.calculate_price).
describe('calculatePrice', () => {
  it('uses the hourly rate for a short booking (under 24h)', () => {
    const price = calculatePrice(
      1000,
      100,
      new Date('2026-09-01T08:00:00'),
      new Date('2026-09-01T10:00:00'),
    )
    expect(price).toBe(200)
  })

  it('caps a long partial day at the daily rate', () => {
    const price = calculatePrice(
      1000,
      100,
      new Date('2026-09-01T08:00:00'),
      new Date('2026-09-01T20:00:00'),
    )
    expect(price).toBe(1000)
  })

  it('combines full day(s) with a capped remainder for a multi-day booking', () => {
    const price = calculatePrice(
      1000,
      100,
      new Date('2026-09-01T08:00:00'),
      new Date('2026-09-03T11:00:00'),
    )
    expect(price).toBe(2300)
  })

  it('returns 0 when the range is empty or inverted', () => {
    const start = new Date('2026-09-01T10:00:00')
    const end = new Date('2026-09-01T08:00:00')
    expect(calculatePrice(1000, 100, start, end)).toBe(0)
  })
})

describe('formatDuration', () => {
  it('formats a duration under a day in hours only', () => {
    expect(
      formatDuration(new Date('2026-09-01T08:00:00'), new Date('2026-09-01T11:00:00')),
    ).toBe('3 hodiny')
  })

  it('formats a multi-day duration with both days and hours', () => {
    expect(
      formatDuration(new Date('2026-09-01T08:00:00'), new Date('2026-09-03T11:00:00')),
    ).toBe('2 dny 3 hodiny')
  })

  it('returns an empty string for a non-positive duration', () => {
    expect(
      formatDuration(new Date('2026-09-01T10:00:00'), new Date('2026-09-01T08:00:00')),
    ).toBe('')
  })
})
