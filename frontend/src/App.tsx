import { useEffect, useState } from 'react'
import type { Car, Reservation } from './api'
import { fetchCars, fetchReservations } from './api'
import CarList from './components/CarList'
import ReservationForm from './components/ReservationForm'
import ReservationList from './components/ReservationList'
import './App.css'

type Tab = 'cars' | 'reservations'

function App() {
  const [tab, setTab] = useState<Tab>('cars')
  const [cars, setCars] = useState<Car[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [selectedCar, setSelectedCar] = useState<Car | null>(null)
  const [confirmation, setConfirmation] = useState<string | null>(null)

  const [reservations, setReservations] = useState<Reservation[]>([])
  const [reservationsLoading, setReservationsLoading] = useState(false)
  const [reservationsError, setReservationsError] = useState<string | null>(null)

  useEffect(() => {
    fetchCars()
      .then(setCars)
      .catch((err) =>
        setLoadError(err instanceof Error ? err.message : 'Nepodařilo se načíst auta'),
      )
      .finally(() => setLoading(false))
  }, [])

  function loadReservations() {
    setReservationsLoading(true)
    setReservationsError(null)
    fetchReservations()
      .then(setReservations)
      .catch((err) =>
        setReservationsError(
          err instanceof Error ? err.message : 'Nepodařilo se načíst rezervace',
        ),
      )
      .finally(() => setReservationsLoading(false))
  }

  useEffect(() => {
    if (tab === 'reservations') {
      loadReservations()
    }
  }, [tab])

  function handleReservationDone() {
    setSelectedCar(null)
    setConfirmation('Rezervace byla úspěšně vytvořena!')
  }

  return (
    <div className="page">
      <header>
        <h1>CarRentalVSB</h1>
        <p>Rezervační systém půjčovny aut</p>
      </header>

      <nav className="tabs">
        <button
          type="button"
          className={tab === 'cars' ? 'active' : ''}
          onClick={() => setTab('cars')}
        >
          Dostupná auta
        </button>
        <button
          type="button"
          className={tab === 'reservations' ? 'active' : ''}
          onClick={() => setTab('reservations')}
        >
          Moje rezervace
        </button>
      </nav>

      <main>
        {tab === 'cars' ? (
          <>
            {confirmation && <p className="confirmation">{confirmation}</p>}

            {selectedCar ? (
              <ReservationForm
                car={selectedCar}
                onDone={handleReservationDone}
                onCancel={() => setSelectedCar(null)}
              />
            ) : (
              <>
                <h2>Dostupná auta</h2>
                {loading && <p>Načítám auta…</p>}
                {loadError && <p className="error">{loadError}</p>}
                {!loading && !loadError && (
                  <CarList cars={cars} onReserve={setSelectedCar} />
                )}
              </>
            )}
          </>
        ) : (
          <>
            <h2>Moje rezervace</h2>
            {reservationsLoading && <p>Načítám rezervace…</p>}
            {reservationsError && <p className="error">{reservationsError}</p>}
            {!reservationsLoading && !reservationsError && (
              <ReservationList
                reservations={reservations}
                cars={cars}
                onChanged={loadReservations}
              />
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
