import { useEffect, useState } from 'react'
import type { Car, PaymentMethod } from '../api'
import { checkAvailability, createReservation } from '../api'
import { useAuth } from '../auth/AuthContext'
import { calculatePrice, formatDuration } from '../pricing'
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

function nowLocalInputValue(): string {
  const now = new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
  return now.toISOString().slice(0, 16)
}

export default function ReservationForm({ car, onDone, onCancel }: Props) {
  const { token } = useAuth()
  const { show } = useToast()
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('CASH')
  const [cardNumber, setCardNumber] = useState('')
  const [cardExpiry, setCardExpiry] = useState('')
  const [cardCvc, setCardCvc] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [availability, setAvailability] = useState<AvailabilityState>({ status: 'idle' })

  const validRange = Boolean(startDate) && Boolean(endDate) && new Date(endDate) > new Date(startDate)
  const estimatedPrice = validRange
    ? calculatePrice(car.daily_price, car.hourly_price, new Date(startDate), new Date(endDate))
    : null
  const duration = validRange ? formatDuration(new Date(startDate), new Date(endDate)) : ''

  useEffect(() => {
    if (!startDate || !endDate) {
      setAvailability({ status: 'idle' })
      return
    }
    if (new Date(endDate) <= new Date(startDate)) {
      setAvailability({ status: 'error', message: 'Termín "vrácení" musí být po termínu "vyzvednutí"' })
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
      // Card details are never sent anywhere — this is a mock payment step;
      // only the chosen method is part of the actual reservation.
      await createReservation(token, {
        car_id: car.id,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
        payment_method: paymentMethod,
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
        <span>
          {car.daily_price.toLocaleString('cs-CZ')} Kč/den · {car.hourly_price.toLocaleString('cs-CZ')} Kč/h
        </span>
      </div>

      <div className="date-row">
        <label>
          Vyzvednutí
          <input
            type="datetime-local"
            required
            min={nowLocalInputValue()}
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>
        <label>
          Vrácení
          <input
            type="datetime-local"
            required
            min={startDate || nowLocalInputValue()}
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
      </div>

      <p className="hint">
        Denní sazba platí za každých 24 hodin od vyzvednutí — auto vracíte přesně v čas, který
        zvolíte jako "Vrácení". Kratší výpůjčky se počítají po hodinách, ale nikdy nepřesáhnou
        cenu za celý den.
      </p>

      {availability.status === 'checking' && <p className="hint">Kontroluji dostupnost…</p>}
      {availability.status === 'available' && (
        <p className="availability-ok">Termín je dostupný</p>
      )}
      {availability.status === 'unavailable' && (
        <p className="error">Auto je v tomto termínu již obsazené</p>
      )}
      {availability.status === 'error' && <p className="error">{availability.message}</p>}

      {estimatedPrice !== null && (
        <div className="price-estimate">
          <span>Doba zápůjčky: {duration}</span>
          <strong>{estimatedPrice.toLocaleString('cs-CZ')} Kč</strong>
        </div>
      )}

      <div className="payment-method">
        <span className="payment-method-label">Způsob platby</span>
        <div className="payment-method-options">
          <label className="payment-option">
            <input
              type="radio"
              name="payment-method"
              checked={paymentMethod === 'CASH'}
              onChange={() => setPaymentMethod('CASH')}
            />
            Hotově
          </label>
          <label className="payment-option">
            <input
              type="radio"
              name="payment-method"
              checked={paymentMethod === 'CARD'}
              onChange={() => setPaymentMethod('CARD')}
            />
            Kartou
          </label>
        </div>
      </div>

      {paymentMethod === 'CARD' && (
        <div className="card-form">
          <label>
            Číslo karty
            <input
              type="text"
              required
              inputMode="numeric"
              placeholder="1234 5678 9012 3456"
              maxLength={19}
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
            />
          </label>
          <div className="date-row">
            <label>
              Platnost
              <input
                type="text"
                required
                placeholder="MM/RR"
                maxLength={5}
                value={cardExpiry}
                onChange={(e) => setCardExpiry(e.target.value)}
              />
            </label>
            <label>
              CVC
              <input
                type="text"
                required
                inputMode="numeric"
                placeholder="123"
                maxLength={3}
                value={cardCvc}
                onChange={(e) => setCardCvc(e.target.value)}
              />
            </label>
          </div>
          <p className="hint">Toto je testovací formulář — údaje o kartě se nikam neodesílají.</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      <div className="form-actions">
        <button type="submit" disabled={submitting || availability.status === 'unavailable'}>
          {submitting
            ? 'Odesílám…'
            : paymentMethod === 'CARD'
              ? 'Zaplatit a rezervovat'
              : 'Potvrdit rezervaci'}
        </button>
        <button type="button" className="secondary" onClick={onCancel} disabled={submitting}>
          Zrušit
        </button>
      </div>
    </form>
  )
}
