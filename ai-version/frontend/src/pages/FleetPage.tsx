import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, type Branch, type Car, type CarData } from '../api/client';
import { formatPrice, Message } from '../components/common';
import { CAR_OPTIONS } from '../carOptions';
import { carLabel } from '../labels';

const emptyCar = (branchId: number): CarData => ({
  brand: '',
  model: '',
  year: new Date().getFullYear(),
  license_plate: '',
  daily_price: 1000,
  hourly_price: 120,
  category: 'Hatchback',
  transmission: 'Manual',
  fuel_type: 'Petrol',
  seats: 5,
  description: '',
  image_url: '',
  branch_id: branchId,
});

const toData = (car: Car): CarData => {
  const { id: _id, branch: _branch, ...data } = car;
  return data;
};

/** UC9 Manage fleet - add / edit / delete cars. */
export function FleetPage() {
  const [cars, setCars] = useState<Car[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [editing, setEditing] = useState<{ id: number | null; data: CarData } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const reload = useCallback(() => {
    Promise.all([api.cars(), api.branches()])
      .then(([carList, branchList]) => {
        setCars(carList);
        setBranches(branchList);
      })
      .catch((e: Error) => setError(e.message));
  }, []);
  useEffect(reload, [reload]);

  const save = async (e: FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    setError(null);
    try {
      if (editing.id === null) {
        await api.createCar(editing.data);
        setNotice('Auto bylo přidáno.');
      } else {
        await api.updateCar(editing.id, editing.data);
        setNotice('Auto bylo upraveno.');
      }
      setEditing(null);
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Uložení selhalo');
    }
  };

  const remove = async (car: Car) => {
    if (!window.confirm(`Smazat ${car.brand} ${car.model} (${car.license_plate}) včetně všech jeho rezervací?`)) return;
    setError(null);
    try {
      await api.deleteCar(car.id);
      setNotice('Auto bylo smazáno včetně jeho rezervací.');
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Smazání selhalo');
    }
  };

  const field = <K extends keyof CarData>(key: K, label: string, type: 'text' | 'number' = 'text') => (
    <label>
      {label}
      <input
        type={type}
        value={editing?.data[key] ?? ''}
        step={type === 'number' ? 'any' : undefined}
        required={key !== 'description' && key !== 'image_url'}
        onChange={(e) =>
          editing &&
          setEditing({
            ...editing,
            data: { ...editing.data, [key]: type === 'number' ? Number(e.target.value) : e.target.value },
          })
        }
      />
    </label>
  );

  const selectField = (key: keyof typeof CAR_OPTIONS, label: string) => (
    <label>
      {label}
      <select
        value={editing?.data[key] ?? ''}
        required
        onChange={(e) => editing && setEditing({ ...editing, data: { ...editing.data, [key]: e.target.value } })}
      >
        {CAR_OPTIONS[key].map((value) => (
          <option key={value} value={value}>
            {carLabel(value)}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <section>
      <div className="section-head">
        <h1>Správa vozového parku</h1>
        <button
          onClick={() => {
            setNotice(null);
            setEditing({ id: null, data: emptyCar(branches[0]?.id ?? 0) });
          }}
          disabled={!branches.length}
        >
          Přidat auto
        </button>
      </div>
      {notice && <Message kind="success">{notice}</Message>}
      {error && <Message kind="error">{error}</Message>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Auto</th>
              <th>SPZ</th>
              <th>Kategorie</th>
              <th>Převodovka / palivo</th>
              <th>Cena</th>
              <th>Pobočka</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {cars.map((car) => (
              <tr key={car.id}>
                <td>
                  {car.brand} {car.model} <span className="muted">({car.year})</span>
                </td>
                <td>{car.license_plate}</td>
                <td>{carLabel(car.category)}</td>
                <td>
                  {carLabel(car.transmission)} / {carLabel(car.fuel_type)}
                </td>
                <td className="small">
                  {formatPrice(car.daily_price)} / den
                  <br />
                  {formatPrice(car.hourly_price)} / hod
                </td>
                <td>{car.branch.name}</td>
                <td className="actions">
                  <button
                    className="secondary"
                    onClick={() => {
                      setNotice(null);
                      setEditing({ id: car.id, data: toData(car) });
                    }}
                  >
                    Upravit
                  </button>
                  <button className="danger" onClick={() => void remove(car)}>
                    Smazat
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing && (
        <div className="modal-backdrop" onClick={() => setEditing(null)}>
          <form className="modal wide" onClick={(e) => e.stopPropagation()} onSubmit={save}>
            <div className="modal-head">
              <h2>{editing.id === null ? 'Nové auto' : 'Upravit auto'}</h2>
              <button type="button" className="icon-button" onClick={() => setEditing(null)} aria-label="Zavřít">
                ×
              </button>
            </div>
            {error && <Message kind="error">{error}</Message>}
            <div className="grid-3">
              {field('brand', 'Značka')}
              {field('model', 'Model')}
              {field('year', 'Rok výroby', 'number')}
              {field('license_plate', 'SPZ')}
              {field('daily_price', 'Cena za den (Kč)', 'number')}
              {field('hourly_price', 'Cena za hodinu (Kč)', 'number')}
              {selectField('category', 'Kategorie')}
              {selectField('transmission', 'Převodovka')}
              {selectField('fuel_type', 'Palivo')}
              {field('seats', 'Počet míst', 'number')}
              <label>
                Pobočka
                <select
                  value={editing.data.branch_id}
                  onChange={(e) =>
                    setEditing({ ...editing, data: { ...editing.data, branch_id: Number(e.target.value) } })
                  }
                >
                  {branches.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </label>
              {field('image_url', 'URL fotky (nepovinné)')}
            </div>
            {field('description', 'Popis')}
            <div className="modal-actions">
              <button type="button" className="secondary" onClick={() => setEditing(null)}>
                Zrušit
              </button>
              <button type="submit">Uložit</button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}
