import { useState } from 'react'
import type { Reservation } from '../api'
import { cancelReservation } from '../api'
import { useAuth } from '../auth/AuthContext'
import { PAYMENT_METHOD_LABELS, STATUS_LABELS } from '../constants'
import { useToast } from './Toast'

interface Props {
  reservations: Reservation[]
  onChanged: () => void
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString('cs-CZ', {
    day: 'numeric',
    month: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function ReservationList({ reservations, onChanged }: Props) {
  const { token } = useAuth()
  const { show } = useToast()
  const [pendingId, setPendingId] = useState<number | null>(null)

  async function handleCancel(id: number) {
    if (!token) return
    setPendingId(id)
    try {
      await cancelReservation(token, id)
      show('Rezervace byla zrušena.', 'success')
      onChanged()
    } catch (err) {
      show(err instanceof Error ? err.message : 'Zrušení se nezdařilo', 'error')
    } finally {
      setPendingId(null)
    }
  }

  if (reservations.length === 0) {
    return <p className="empty-state">Zatím nemáte žádné rezervace.</p>
  }

  return (
    <ul className="reservation-list">
      {reservations.map((reservation) => (
        <li key={reservation.id} className="reservation-card">
          <div className="reservation-info">
            <strong>
              {reservation.car.brand} {reservation.car.model}
            </strong>
            <div className="dates">
              {formatDateTime(reservation.start_date)} – {formatDateTime(reservation.end_date)}
            </div>
            <div className="reservation-price">
              {reservation.total_price.toLocaleString('cs-CZ')} Kč ·{' '}
              {PAYMENT_METHOD_LABELS[reservation.payment_method]}
            </div>
            <span className={`status-badge status-${reservation.status.toLowerCase()}`}>
              {STATUS_LABELS[reservation.status]}
            </span>
          </div>

          <div className="reservation-actions">
            {reservation.status !== 'CANCELLED' && (
              <button
                type="button"
                className="secondary"
                onClick={() => handleCancel(reservation.id)}
                disabled={pendingId === reservation.id}
              >
                Zrušit
              </button>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}
