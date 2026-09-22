import { useEffect, useState } from 'react'
import type { Car } from '../api'
import { checkAvailability, createReservation } from '../api'
import { useAuth } from '../auth/AuthContext'
import { useToast } from './Toast'

interface Props {
  car: Car
  onDone: () => void
  onCancel: () => void
}

type AvailabilityState =
  | { status: 'idle' }
  | { status: 'checking' }
  | { status: 'available' }
  | { status: 'unavailable' }
  | { status: 'error'; message: string }

export default function ReservationForm({ car, onDone, onCancel }: Props) {
  const { token } = useAuth()
  const { show } = useToast()
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [availability, setAvailability] = useState<AvailabilityState>({ status: 'idle' })

  useEffect(() => {
    if (!startDate || !endDate) {
      setAvailability({ status: 'idle' })
      return
    }
    if (new Date(endDate) <= new Date(startDate)) {
      setAvailability({ status: 'error', message: 'Datum "do" musí být po datu "od"' })
      return
    }

    let cancelled = false
    setAvailability({ status: 'checking' })
    const timeout = setTimeout(() => {
      checkAvailability(
        car.id,
        new Date(startDate).toISOString(),
        new Date(endDate).toISOString(),
      )
        .then((result) => {
          if (!cancelled) {
            setAvailability({ status: result.available ? 'available' : 'unavailable' })
          }
        })
        .catch((err) => {
          if (!cancelled) {
            setAvailability({
              status: 'error',
              message:
                err instanceof Error ? err.message : 'Kontrolu dostupnosti se nepodařilo provést',
            })
          }
        })
    }, 300)

    return () => {
      cancelled = true
      clearTimeout(timeout)
    }
  }, [car.id, startDate, endDate])

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!token) return
    setError(null)
    setSubmitting(true)
    try {
      await createReservation(token, {
        car_id: car.id,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
      })
      show('Rezervace byla úspěšně vytvořena.', 'success')
      onDone()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Neznámá chyba'
      setError(message)
      show(message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="reservation-form" onSubmit={handleSubmit}>
      <div className="reservation-form-summary">
        <strong>
          {car.brand} {car.model}
        </strong>
        <span>{car.daily_price.toLocaleString('cs-CZ')} Kč / den</span>
      </div>

      <div className="date-row">
        <label>
          Od
          <input
            type="date"
            required
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>
        <label>
          Do
          <input
            type="date"
            required
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
      </div>

      {availability.status === 'checking' && <p className="hint">Kontroluji dostupnost…</p>}
      {availability.status === 'available' && (
        <p className="availability-ok">Termín je dostupný</p>
      )}
      {availability.status === 'unavailable' && (
        <p className="error">Auto je v tomto termínu již obsazené</p>
      )}
      {availability.status === 'error' && <p className="error">{availability.message}</p>}

      {error && <p className="error">{error}</p>}

      <div className="form-actions">
        <button type="submit" disabled={submitting || availability.status === 'unavailable'}>
          {submitting ? 'Odesílám…' : 'Potvrdit rezervaci'}
        </button>
        <button type="button" className="secondary" onClick={onCancel} disabled={submitting}>
          Zrušit
        </button>
      </div>
    </form>
  )
}
