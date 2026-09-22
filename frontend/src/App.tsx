import { useEffect, useState } from 'react'
import type { Car, Reservation } from './api'
import { fetchAllReservations, fetchCars, fetchMyReservations } from './api'
import { AuthProvider, useAuth } from './auth/AuthContext'
import { ToastProvider } from './components/Toast'
import Navbar from './components/Navbar'
import CarGrid from './components/CarGrid'
import CarFilters, { EMPTY_FILTERS } from './components/CarFilters'
import type { FiltersState } from './components/CarFilters'
import ReservationForm from './components/ReservationForm'
import ReservationList from './components/ReservationList'
import AdminCars from './components/AdminCars'
import AdminReservations from './components/AdminReservations'
import AuthForms from './components/AuthForms'
import Modal from './components/Modal'
import SupportWidget from './components/SupportWidget'
import './App.css'

export type Tab = 'cars' | 'my-reservations' | 'admin-cars' | 'admin-reservations'

function AppContent() {
  const { user, token, loading: authLoading } = useAuth()
  const [tab, setTab] = useState<Tab>('cars')

  const [cars, setCars] = useState<Car[]>([])
  const [carsLoading, setCarsLoading] = useState(true)
  const [carsError, setCarsError] = useState<string | null>(null)
  const [filters, setFilters] = useState<FiltersState>(EMPTY_FILTERS)

  const [myReservations, setMyReservations] = useState<Reservation[]>([])
  const [myReservationsLoading, setMyReservationsLoading] = useState(false)

  const [allReservations, setAllReservations] = useState<Reservation[]>([])
  const [allReservationsLoading, setAllReservationsLoading] = useState(false)

  const [bookingCar, setBookingCar] = useState<Car | null>(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [pendingReserveCar, setPendingReserveCar] = useState<Car | null>(null)

  useEffect(() => {
    const timeout = setTimeout(() => {
      setCarsLoading(true)
      setCarsError(null)
      fetchCars({
        category: filters.category || undefined,
        transmission: filters.transmission || undefined,
        fuel_type: filters.fuelType || undefined,
        min_price: filters.minPrice ? Number(filters.minPrice) : undefined,
        max_price: filters.maxPrice ? Number(filters.maxPrice) : undefined,
      })
        .then(setCars)
        .catch((err) =>
          setCarsError(err instanceof Error ? err.message : 'Nepodařilo se načíst auta'),
        )
        .finally(() => setCarsLoading(false))
    }, 250)
    return () => clearTimeout(timeout)
  }, [filters])

  function loadMyReservations() {
    if (!token) return
    setMyReservationsLoading(true)
    fetchMyReservations(token)
      .then(setMyReservations)
      .finally(() => setMyReservationsLoading(false))
  }

  function loadAllReservations() {
    if (!token) return
    setAllReservationsLoading(true)
    fetchAllReservations(token)
      .then(setAllReservations)
      .finally(() => setAllReservationsLoading(false))
  }

  useEffect(() => {
    if (tab === 'my-reservations') loadMyReservations()
    if (tab === 'admin-reservations') loadAllReservations()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, token])

  useEffect(() => {
    if (user && pendingReserveCar) {
      setBookingCar(pendingReserveCar)
      setPendingReserveCar(null)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  function handleReserveClick(car: Car) {
    if (!user) {
      setPendingReserveCar(car)
      setAuthModalOpen(true)
      return
    }
    setBookingCar(car)
  }

  function handleBookingDone() {
    setBookingCar(null)
    if (tab === 'my-reservations') loadMyReservations()
  }

  if (authLoading) {
    return <div className="page-loading">Načítám…</div>
  }

  return (
    <div className="app-shell">
      <Navbar tab={tab} onTabChange={setTab} onAuthOpen={() => setAuthModalOpen(true)} />

      <main className="page">
        {tab === 'cars' && (
          <>
            <div className="hero">
              <h1>Najdi si auto na míru</h1>
              <p>Vyber si z {cars.length} vozů podle kategorie, převodovky, paliva i ceny.</p>
            </div>

            <CarFilters filters={filters} onChange={setFilters} />

            {carsLoading && <p className="hint">Načítám auta…</p>}
            {carsError && <p className="error">{carsError}</p>}
            {!carsLoading && !carsError && <CarGrid cars={cars} onReserve={handleReserveClick} />}
          </>
        )}

        {tab === 'my-reservations' && user && (
          <>
            <h2>Moje rezervace</h2>
            {myReservationsLoading ? (
              <p className="hint">Načítám rezervace…</p>
            ) : (
              <ReservationList reservations={myReservations} onChanged={loadMyReservations} />
            )}
          </>
        )}

        {tab === 'admin-cars' && user?.role === 'ADMIN' && <AdminCars />}

        {tab === 'admin-reservations' && user?.role === 'ADMIN' && (
          <>
            <h2>Všechny rezervace</h2>
            {allReservationsLoading ? (
              <p className="hint">Načítám rezervace…</p>
            ) : (
              <AdminReservations reservations={allReservations} onChanged={loadAllReservations} />
            )}
          </>
        )}
      </main>

      {bookingCar && (
        <Modal
          title={`Rezervace: ${bookingCar.brand} ${bookingCar.model}`}
          onClose={() => setBookingCar(null)}
        >
          <ReservationForm
            car={bookingCar}
            onDone={handleBookingDone}
            onCancel={() => setBookingCar(null)}
          />
        </Modal>
      )}

      {authModalOpen && (
        <Modal
          title="Účet"
          onClose={() => {
            setAuthModalOpen(false)
            setPendingReserveCar(null)
          }}
        >
          <AuthForms
            onSuccess={() => setAuthModalOpen(false)}
            message={
              pendingReserveCar
                ? 'Pro rezervaci auta se prosím přihlas nebo si vytvoř účet.'
                : undefined
            }
          />
        </Modal>
      )}

      <SupportWidget />
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  )
}

export default App
