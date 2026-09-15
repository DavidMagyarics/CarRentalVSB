import { useEffect, useState } from 'react'
import type { Car } from './api'
import { fetchCars } from './api'
import CarList from './components/CarList'
import ReservationForm from './components/ReservationForm'
import './App.css'

function App() {
  const [cars, setCars] = useState<Car[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [selectedCar, setSelectedCar] = useState<Car | null>(null)
  const [confirmation, setConfirmation] = useState<string | null>(null)

  useEffect(() => {
    fetchCars()
      .then(setCars)
      .catch((err) =>
        setLoadError(err instanceof Error ? err.message : 'Nepodařilo se načíst auta'),
      )
      .finally(() => setLoading(false))
  }, [])

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

      <main>
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
      </main>
    </div>
  )
}

export default App
