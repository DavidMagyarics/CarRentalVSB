import { useState } from 'react'
import type { Car } from '../api'
import { createReservation } from '../api'

interface Props {
  car: Car
  onDone: () => void
  onCancel: () => void
}

export default function ReservationForm({ car, onDone, onCancel }: Props) {
  const [customerName, setCustomerName] = useState('')
  const [customerEmail, setCustomerEmail] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await createReservation({
        car_id: car.id,
        customer_name: customerName,
        customer_email: customerEmail,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
      })
      onDone()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Neznámá chyba')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="reservation-form" onSubmit={handleSubmit}>
      <h3>
        Rezervace: {car.brand} {car.model}
      </h3>

      <label>
        Jméno a příjmení
        <input
          type="text"
          required
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
        />
      </label>

      <label>
        E-mail
        <input
          type="email"
          required
          value={customerEmail}
          onChange={(e) => setCustomerEmail(e.target.value)}
        />
      </label>

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

      {error && <p className="error">{error}</p>}

      <div className="form-actions">
        <button type="submit" disabled={submitting}>
          {submitting ? 'Odesílám…' : 'Potvrdit rezervaci'}
        </button>
        <button type="button" onClick={onCancel} disabled={submitting}>
          Zrušit
        </button>
      </div>
    </form>
  )
}
