import { useEffect, useState } from 'react'
import type { Car, CarInput } from '../api'
import { createCar, deleteCar, fetchCars, updateCar } from '../api'
import { useAuth } from '../auth/AuthContext'
import { CATEGORY_LABELS, FUEL_LABELS, TRANSMISSION_LABELS } from '../constants'
import { useToast } from './Toast'
import Modal from './Modal'

const EMPTY_FORM: CarInput = {
  brand: '',
  model: '',
  year: new Date().getFullYear(),
  license_plate: '',
  daily_price: 0,
  hourly_price: 0,
  category: 'SEDAN',
  transmission: 'MANUAL',
  fuel_type: 'PETROL',
  seats: 5,
  description: '',
  image_url: '',
}

export default function AdminCars() {
  const { token } = useAuth()
  const { show } = useToast()

  const [cars, setCars] = useState<Car[]>([])
  const [loading, setLoading] = useState(true)

  const [editing, setEditing] = useState<Car | null>(null)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState<CarInput>(EMPTY_FORM)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function load() {
    setLoading(true)
    fetchCars({})
      .then(setCars)
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  function openCreate() {
    setForm(EMPTY_FORM)
    setError(null)
    setCreating(true)
  }

  function openEdit(car: Car) {
    setForm({
      brand: car.brand,
      model: car.model,
      year: car.year,
      license_plate: car.license_plate,
      daily_price: car.daily_price,
      hourly_price: car.hourly_price,
      category: car.category,
      transmission: car.transmission,
      fuel_type: car.fuel_type,
      seats: car.seats,
      description: car.description ?? '',
      image_url: car.image_url ?? '',
    })
    setError(null)
    setEditing(car)
  }

  function closeModal() {
    setCreating(false)
    setEditing(null)
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!token) return
    setSubmitting(true)
    setError(null)
    try {
      if (editing) {
        await updateCar(token, editing.id, form)
        show('Auto bylo upraveno.', 'success')
      } else {
        await createCar(token, form)
        show('Auto bylo přidáno.', 'success')
      }
      closeModal()
      load()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Uložení se nezdařilo'
      setError(message)
      show(message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(car: Car) {
    if (!token) return
    if (!window.confirm(`Opravdu smazat ${car.brand} ${car.model}?`)) return
    try {
      await deleteCar(token, car.id)
      show('Auto bylo smazáno.', 'success')
      load()
    } catch (err) {
      show(err instanceof Error ? err.message : 'Smazání se nezdařilo', 'error')
    }
  }

  return (
    <div>
      <div className="admin-toolbar">
        <h2>Vozový park</h2>
        <button type="button" onClick={openCreate}>
          + Přidat auto
        </button>
      </div>

      {loading ? (
        <p className="hint">Načítám auta…</p>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Auto</th>
                <th>Kategorie</th>
                <th>Cena</th>
                <th>SPZ</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {cars.map((car) => (
                <tr key={car.id}>
                  <td>
                    {car.brand} {car.model} ({car.year})
                  </td>
                  <td>{CATEGORY_LABELS[car.category]}</td>
                  <td>
                    {car.daily_price.toLocaleString('cs-CZ')} Kč/den
                    <br />
                    <span className="text-muted">{car.hourly_price.toLocaleString('cs-CZ')} Kč/h</span>
                  </td>
                  <td>{car.license_plate}</td>
                  <td className="admin-table-actions">
                    <button type="button" onClick={() => openEdit(car)}>
                      Upravit
                    </button>
                    <button type="button" className="secondary" onClick={() => handleDelete(car)}>
                      Smazat
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(creating || editing) && (
        <Modal title={editing ? 'Upravit auto' : 'Přidat auto'} onClose={closeModal}>
          <form className="admin-car-form" onSubmit={handleSubmit}>
            <div className="form-grid">
              <label>
                Značka
                <input
                  required
                  value={form.brand}
                  onChange={(e) => setForm({ ...form, brand: e.target.value })}
                />
              </label>
              <label>
                Model
                <input
                  required
                  value={form.model}
                  onChange={(e) => setForm({ ...form, model: e.target.value })}
                />
              </label>
              <label>
                Rok
                <input
                  type="number"
                  required
                  value={form.year}
                  onChange={(e) => setForm({ ...form, year: Number(e.target.value) })}
                />
              </label>
              <label>
                SPZ
                <input
                  required
                  value={form.license_plate}
                  onChange={(e) => setForm({ ...form, license_plate: e.target.value })}
                />
              </label>
              <label>
                Cena/den (Kč)
                <input
                  type="number"
                  required
                  min={0}
                  value={form.daily_price}
                  onChange={(e) => setForm({ ...form, daily_price: Number(e.target.value) })}
                />
              </label>
              <label>
                Cena/hodina (Kč)
                <input
                  type="number"
                  required
                  min={0}
                  value={form.hourly_price}
                  onChange={(e) => setForm({ ...form, hourly_price: Number(e.target.value) })}
                />
              </label>
              <label>
                Počet míst
                <input
                  type="number"
                  required
                  min={1}
                  max={9}
                  value={form.seats}
                  onChange={(e) => setForm({ ...form, seats: Number(e.target.value) })}
                />
              </label>
              <label>
                Kategorie
                <select
                  value={form.category}
                  onChange={(e) =>
                    setForm({ ...form, category: e.target.value as CarInput['category'] })
                  }
                >
                  {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Převodovka
                <select
                  value={form.transmission}
                  onChange={(e) =>
                    setForm({ ...form, transmission: e.target.value as CarInput['transmission'] })
                  }
                >
                  {Object.entries(TRANSMISSION_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Palivo
                <select
                  value={form.fuel_type}
                  onChange={(e) =>
                    setForm({ ...form, fuel_type: e.target.value as CarInput['fuel_type'] })
                  }
                >
                  {Object.entries(FUEL_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label>
              Popis
              <textarea
                rows={2}
                value={form.description ?? ''}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </label>

            <label>
              URL fotky (nepovinné)
              <input
                type="text"
                placeholder="/cars/moje-auto.jpg nebo https://…"
                value={form.image_url ?? ''}
                onChange={(e) => setForm({ ...form, image_url: e.target.value })}
              />
            </label>
            <p className="hint">Bez fotky se zobrazí ilustrace podle kategorie.</p>

            {error && <p className="error">{error}</p>}

            <div className="form-actions">
              <button type="submit" disabled={submitting}>
                {submitting ? 'Ukládám…' : 'Uložit'}
              </button>
              <button type="button" className="secondary" onClick={closeModal}>
                Zrušit
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
