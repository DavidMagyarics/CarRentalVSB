import { useEffect, useReducer, useState, type FormEvent } from 'react';
import { api, ApiError, type Car, type PaymentMethod } from '../api/client';
import { initialFormState, isCardExpiryValid, reservationFormReducer } from '../state/reservationForm';
import { CarImage, formatPrice, Message } from './common';

interface Props {
  car: Car;
  onClose: () => void; // cancel() / close the form
  onCreated: () => void; // [201 Created] / show success, close the form
}

const CHECK_DELAY_MS = 300; // do / is_car_available() (after 300 ms)

/** UC4 Create reservation - the ReservationForm of the class diagram. */
export function ReservationForm({ car, onClose, onCreated }: Props) {
  const [state, dispatch] = useReducer(reservationFormReducer, initialFormState);
  const [card, setCard] = useState({ number: '', expiry: '', cvc: '' });

  // Checking: call the backend availability check (UC4a) after 300 ms.
  useEffect(() => {
    if (state.phase !== 'checking') return;
    const checkId = state.checkId;
    const timer = window.setTimeout(() => {
      api
        .availability(car.id, state.start, state.end)
        .then((r) => dispatch({ type: 'check_result', checkId, available: r.available }))
        .catch((e: unknown) =>
          dispatch({
            type: 'check_failed',
            checkId,
            error: e instanceof Error ? e.message : 'Kontrola dostupnosti selhala.',
          }),
        );
    }, CHECK_DELAY_MS);
    return () => window.clearTimeout(timer);
  }, [state.phase, state.checkId, state.start, state.end, car.id]);

  // Submitting: entry / create_reservation(c, start, end, payment)
  useEffect(() => {
    if (state.phase !== 'submitting') return;
    let active = true;
    api
      .createReservation(car.id, state.start, state.end, state.payment)
      .then(() => active && dispatch({ type: 'submit_succeeded' }))
      .catch((e: unknown) => {
        if (!active) return;
        const message =
          e instanceof ApiError ? e.message : 'Rezervaci se nepodařilo vytvořit.';
        dispatch({ type: 'submit_failed', error: message });
      });
    return () => {
      active = false;
    };
  }, [state.phase, state.start, state.end, state.payment, car.id]);

  useEffect(() => {
    if (state.phase === 'done') onCreated();
  }, [state.phase, onCreated]);

  const enterDates = (start: string, end: string) =>
    dispatch({ type: 'enter_dates', start, end, now: new Date(), prices: [car.daily_price, car.hourly_price] });

  // Mock card details - validated in the browser only, never sent to the server.
  const cardValid =
    /^\d{16}$/.test(card.number.replace(/\s/g, '')) &&
    isCardExpiryValid(card.expiry, new Date()) &&
    /^\d{3}$/.test(card.cvc);
  const canSubmit = state.phase === 'available' && (state.payment === 'CASH' || cardValid);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (canSubmit) dispatch({ type: 'submit' });
  };

  const choosePayment = (method: PaymentMethod) => dispatch({ type: 'choose_payment', method });
  const busy = state.phase === 'submitting';

  return (
    <div className="modal-backdrop" onClick={busy ? undefined : onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <div className="modal-head">
          <h2>
            Rezervace: {car.brand} {car.model}
          </h2>
          <button type="button" className="icon-button" onClick={onClose} disabled={busy} aria-label="Zavřít">
            ×
          </button>
        </div>

        <div className="reserve-car">
          <CarImage src={car.image_url} label={`${car.brand} ${car.model}`} small />
          <div>
            <div>{car.branch.name}</div>
            <div className="muted">
              {formatPrice(car.daily_price)} / den · {formatPrice(car.hourly_price)} / hod
            </div>
          </div>
        </div>

        <p className="muted small">Vyzvednutí i vrácení: pracovní dny (Po–Pá) 8:00–20:00.</p>
        <div className="grid-2">
          <label>
            Vyzvednutí
            <input
              type="datetime-local"
              value={state.start}
              disabled={busy}
              onChange={(e) => enterDates(e.target.value, state.end)}
              required
            />
          </label>
          <label>
            Vrácení
            <input
              type="datetime-local"
              value={state.end}
              disabled={busy}
              onChange={(e) => enterDates(state.start, e.target.value)}
              required
            />
          </label>
        </div>

        {state.phase === 'empty' && <Message kind="info">Zvolte termín vyzvednutí a vrácení.</Message>}
        {state.phase === 'invalid' && state.error && <Message kind="error">{state.error}</Message>}
        {state.phase === 'checking' && <Message kind="info">Ověřuji dostupnost…</Message>}
        {state.phase === 'unavailable' && (
          <Message kind="error">Auto je v tomto termínu již obsazeno. Zvolte jiný termín.</Message>
        )}
        {(state.phase === 'available' || state.phase === 'submitting') && (
          <Message kind="success">
            Termín je dostupný · odhad ceny: <strong>{formatPrice(state.estimate ?? 0)}</strong>
          </Message>
        )}
        {state.phase === 'available' && state.error && <Message kind="error">{state.error}</Message>}

        {(state.phase === 'available' || state.phase === 'submitting') && (
          <fieldset className="payment" disabled={busy}>
            <legend>Způsob platby</legend>
            <label className="inline">
              <input type="radio" checked={state.payment === 'CASH'} onChange={() => choosePayment('CASH')} /> Hotově
              při vyzvednutí
            </label>
            <label className="inline">
              <input type="radio" checked={state.payment === 'CARD'} onChange={() => choosePayment('CARD')} /> Kartou
            </label>
            {state.payment === 'CARD' && (
              <div className="card-fields">
                <p className="muted small">Ukázková platba – údaje karty se na server neodesílají.</p>
                <input
                  placeholder="Číslo karty (16 číslic)"
                  inputMode="numeric"
                  value={card.number}
                  onChange={(e) => setCard({ ...card, number: e.target.value })}
                />
                <div className="grid-2">
                  <input
                    placeholder="MM/RR"
                    value={card.expiry}
                    onChange={(e) => setCard({ ...card, expiry: e.target.value })}
                  />
                  <input
                    placeholder="CVC"
                    inputMode="numeric"
                    value={card.cvc}
                    onChange={(e) => setCard({ ...card, cvc: e.target.value })}
                  />
                </div>
              </div>
            )}
          </fieldset>
        )}

        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose} disabled={busy}>
            Zrušit
          </button>
          <button type="submit" disabled={!canSubmit}>
            {busy ? 'Odesílám…' : 'Odeslat rezervaci'}
          </button>
        </div>
      </form>
    </div>
  );
}
