import { useCallback, useEffect, useState } from 'react';
import { api, type Reservation } from '../api/client';
import { CarImage, formatDate, formatPrice, Message, paymentLabel, StatusBadge } from '../components/common';

const canCancel = (r: Reservation) => r.status !== 'CANCELLED' && !(r.status === 'CONFIRMED' && r.rental_started);

function useReservations(load: () => Promise<Reservation[]>) {
  const [items, setItems] = useState<Reservation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const reload = useCallback(() => {
    load()
      .then((list) => {
        setItems(list);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, [load]);

  useEffect(reload, [reload]);

  const run = async (action: () => Promise<Reservation>, okText: string) => {
    setNotice(null);
    setError(null);
    try {
      await action();
      setNotice(okText);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Akce selhala');
    }
    reload();
  };

  return { items, error, notice, run };
}

/** UC6 View my reservations (+ UC5 Cancel). */
export function MyReservationsPage() {
  const { items, error, notice, run } = useReservations(api.myReservations);

  const cancel = (r: Reservation) => {
    if (window.confirm(`Opravdu zrušit rezervaci č. ${r.id}?`))
      void run(() => api.cancelReservation(r.id), 'Rezervace byla zrušena.');
  };

  return (
    <section>
      <h1>Moje rezervace</h1>
      {notice && <Message kind="success">{notice}</Message>}
      {error && <Message kind="error">{error}</Message>}
      {items && items.length === 0 && <Message kind="info">Zatím nemáte žádné rezervace.</Message>}
      <div className="reservation-list">
        {(items ?? []).map((r) => (
          <article key={r.id} className="reservation-item">
            <CarImage src={r.car.image_url} label={`${r.car.brand} ${r.car.model}`} small />
            <div className="grow">
              <h3>
                {r.car.brand} {r.car.model} <span className="muted small">#{r.id}</span>
              </h3>
              <div className="small">
                {formatDate(r.start_date)} → {formatDate(r.end_date)}
              </div>
              <div className="small">
                {formatPrice(r.total_price)} · {paymentLabel(r.payment_method)}
              </div>
            </div>
            <div className="actions">
              <StatusBadge status={r.status} started={r.rental_started} />
              {canCancel(r) && (
                <button className="danger" onClick={() => cancel(r)}>
                  Zrušit
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

/** UC10 View all reservations (+ UC8 Confirm, UC5 Cancel). */
export function AllReservationsPage() {
  const { items, error, notice, run } = useReservations(api.allReservations);

  const confirm = (r: Reservation) =>
    void run(() => api.confirmReservation(r.id), `Rezervace č. ${r.id} byla potvrzena a zákazník byl informován.`);
  const cancel = (r: Reservation) => {
    if (window.confirm(`Opravdu zrušit rezervaci č. ${r.id}?`))
      void run(() => api.cancelReservation(r.id), `Rezervace č. ${r.id} byla zrušena.`);
  };

  return (
    <section>
      <h1>Všechny rezervace</h1>
      {notice && <Message kind="success">{notice}</Message>}
      {error && <Message kind="error">{error}</Message>}
      {items && items.length === 0 && <Message kind="info">Žádné rezervace.</Message>}
      {items && items.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Auto</th>
                <th>Zákazník</th>
                <th>Termín</th>
                <th>Cena</th>
                <th>Platba</th>
                <th>Stav</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>
                    {r.car.brand} {r.car.model}
                    <div className="muted small">{r.car.license_plate}</div>
                  </td>
                  <td>
                    {r.user.name}
                    <div className="muted small">{r.user.email}</div>
                  </td>
                  <td className="small">
                    {formatDate(r.start_date)}
                    <br />
                    {formatDate(r.end_date)}
                  </td>
                  <td>{formatPrice(r.total_price)}</td>
                  <td>{paymentLabel(r.payment_method)}</td>
                  <td>
                    <StatusBadge status={r.status} started={r.rental_started} />
                  </td>
                  <td className="actions">
                    {r.status === 'DRAFT' && <button onClick={() => confirm(r)}>Potvrdit</button>}
                    {canCancel(r) && (
                      <button className="danger" onClick={() => cancel(r)}>
                        Zrušit
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
