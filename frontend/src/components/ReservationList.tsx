import { useState } from 'react'
import type { Car, Reservation } from '../api'
import { cancelReservation, confirmReservation } from '../api'

interface Props {
  reservations: Reservation[]
  cars: Car[]
  onChanged: () => void
}

const STATUS_LABELS: Record<Reservation['status'], string> = {
  DRAFT: 'Čeká na potvrzení',
  CONFIRMED: 'Potvrzeno',
  CANCELLED: 'Zrušeno',
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('cs-CZ')
}

export default function ReservationList({ reservations, cars, onChanged }: Props) {
  const [pendingId, setPendingId] = useState<number | null>(null)
  const [errors, setErrors] = useState<Record<number, string>>({})

  function carLabel(carId: number) {
    const car = cars.find((c) => c.id === carId)
    return car ? `${car.brand} ${car.model} (${car.license_plate})` : `Auto #${carId}`
  }

  async function handleConfirm(id: number) {
    setPendingId(id)
    setErrors((prev) => ({ ...prev, [id]: '' }))
    try {
      await confirmReservation(id)
      onChanged()
    } catch (err) {
      setErrors((prev) => ({
        ...prev,
        [id]: err instanceof Error ? err.message : 'Potvrzení se nezdařilo',
      }))
    } finally {
      setPendingId(null)
    }
  }

  async function handleCancel(id: number) {
    setPendingId(id)
    setErrors((prev) => ({ ...prev, [id]: '' }))
    try {
      await cancelReservation(id)
      onChanged()
    } catch (err) {
      setErrors((prev) => ({
        ...prev,
        [id]: err instanceof Error ? err.message : 'Zrušení se nezdařilo',
      }))
    } finally {
      setPendingId(null)
    }
  }

  if (reservations.length === 0) {
    return <p>Zatím nemáte žádné rezervace.</p>
  }

  return (
    <ul className="reservation-list">
      {reservations.map((reservation) => (
        <li key={reservation.id} className="reservation-card">
          <div className="reservation-info">
            <strong>{carLabel(reservation.car_id)}</strong>
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

          {errors[reservation.id] && <p className="error">{errors[reservation.id]}</p>}
        </li>
      ))}
    </ul>
  )
}
