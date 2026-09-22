import { useState } from 'react'
import type { Reservation } from '../api'
import { cancelReservation, confirmReservation } from '../api'
import { useAuth } from '../auth/AuthContext'
import { STATUS_LABELS } from '../constants'
import { useToast } from './Toast'

interface Props {
  reservations: Reservation[]
  onChanged: () => void
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('cs-CZ')
}

export default function ReservationList({ reservations, onChanged }: Props) {
  const { token } = useAuth()
  const { show } = useToast()
  const [pendingId, setPendingId] = useState<number | null>(null)

  async function handleConfirm(id: number) {
    if (!token) return
    setPendingId(id)
    try {
      await confirmReservation(token, id)
      show('Rezervace byla potvrzena.', 'success')
      onChanged()
    } catch (err) {
      show(err instanceof Error ? err.message : 'Potvrzení se nezdařilo', 'error')
    } finally {
      setPendingId(null)
    }
  }

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
              {formatDate(reservation.start_date)} – {formatDate(reservation.end_date)}
            </div>
            <span className={`status-badge status-${reservation.status.toLowerCase()}`}>
              {STATUS_LABELS[reservation.status]}
            </span>
          </div>

          <div className="reservation-actions">
            {reservation.status === 'DRAFT' && (
              <button
                type="button"
                onClick={() => handleConfirm(reservation.id)}
                disabled={pendingId === reservation.id}
              >
                Potvrdit
              </button>
            )}
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
