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

export default function AdminReservations({ reservations, onChanged }: Props) {
  const { token } = useAuth()
  const { show } = useToast()
  const [pendingId, setPendingId] = useState<number | null>(null)

  async function act(
    id: number,
    action: (token: string, id: number) => Promise<Reservation>,
    successMessage: string,
  ) {
    if (!token) return
    setPendingId(id)
    try {
      await action(token, id)
      show(successMessage, 'success')
      onChanged()
    } catch (err) {
      show(err instanceof Error ? err.message : 'Akce se nezdařila', 'error')
    } finally {
      setPendingId(null)
    }
  }

  if (reservations.length === 0) {
    return <p className="empty-state">Zatím nejsou žádné rezervace.</p>
  }

  return (
    <div className="admin-table-wrap">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Auto</th>
            <th>Zákazník</th>
            <th>Termín</th>
            <th>Stav</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {reservations.map((reservation) => (
            <tr key={reservation.id}>
              <td>
                {reservation.car.brand} {reservation.car.model}
              </td>
              <td>
                {reservation.user.name}
                <br />
                <span className="text-muted">{reservation.user.email}</span>
              </td>
              <td>
                {formatDate(reservation.start_date)} – {formatDate(reservation.end_date)}
              </td>
              <td>
                <span className={`status-badge status-${reservation.status.toLowerCase()}`}>
                  {STATUS_LABELS[reservation.status]}
                </span>
              </td>
              <td className="admin-table-actions">
                {reservation.status === 'DRAFT' && (
                  <button
                    type="button"
                    onClick={() => act(reservation.id, confirmReservation, 'Rezervace byla potvrzena.')}
                    disabled={pendingId === reservation.id}
                  >
                    Potvrdit
                  </button>
                )}
                {reservation.status !== 'CANCELLED' && (
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => act(reservation.id, cancelReservation, 'Rezervace byla zrušena.')}
                    disabled={pendingId === reservation.id}
                  >
                    Zrušit
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
