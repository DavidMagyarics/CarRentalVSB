import { useCallback, useEffect, useMemo, useState, type ChangeEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api, type Branch, type Car, type CarFilters } from '../api/client';
import { CarImage, formatPrice, Message } from '../components/common';
import { ReservationForm } from '../components/ReservationForm';
import { useAuth } from '../state/auth';
import { carLabel } from '../labels';

const EMPTY_FILTERS: CarFilters = {
  category: '',
  transmission: '',
  fuel_type: '',
  min_price: '',
  max_price: '',
  branch_id: '',
};

const unique = (values: string[]) => [...new Set(values)].sort((a, b) => a.localeCompare(b));

/** UC3 Browse & filter cars (+ entry point of UC4). */
export function CarsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [allCars, setAllCars] = useState<Car[]>([]);
  const [cars, setCars] = useState<Car[] | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [filters, setFilters] = useState<CarFilters>(EMPTY_FILTERS);
  const [error, setError] = useState<string | null>(null);
  const [reserving, setReserving] = useState<Car | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.cars(), api.branches()])
      .then(([carList, branchList]) => {
        setAllCars(carList);
        setBranches(branchList);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  // Query the cars matching the selected filters.
  useEffect(() => {
    const timer = window.setTimeout(() => {
      api
        .cars(filters)
        .then((list) => {
          setCars(list);
          setError(null);
        })
        .catch((e: Error) => setError(e.message));
    }, 200);
    return () => window.clearTimeout(timer);
  }, [filters]);

  // Coming back from the login page with a car to reserve.
  useEffect(() => {
    const carId = (location.state as { reserveCarId?: number } | null)?.reserveCarId;
    if (carId && user && allCars.length) {
      const car = allCars.find((c) => c.id === carId);
      if (car) setReserving(car);
      navigate(location.pathname, { replace: true, state: null });
    }
  }, [location, user, allCars, navigate]);

  const options = useMemo(
    () => ({
      category: unique(allCars.map((c) => c.category)),
      transmission: unique(allCars.map((c) => c.transmission)),
      fuel_type: unique(allCars.map((c) => c.fuel_type)),
    }),
    [allCars],
  );

  const reserve = (car: Car) => {
    setSuccess(null);
    if (!user) {
      // Customer not logged in -> UC2 / UC1, then back here.
      navigate('/login', { state: { from: '/', reserveCarId: car.id } });
      return;
    }
    setReserving(car);
  };

  const onCreated = useCallback(() => {
    setReserving(null);
    setSuccess('Rezervace byla úspěšně vytvořena. Čeká na schválení administrátorem.');
  }, []);

  const set = (key: keyof CarFilters) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setFilters({ ...filters, [key]: e.target.value });

  const selectFilter = (key: 'category' | 'transmission' | 'fuel_type', label: string) => (
    <label>
      {label}
      <select value={filters[key]} onChange={set(key)}>
        <option value="">Vše</option>
        {options[key].map((value) => (
          <option key={value} value={value}>
            {carLabel(value)}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <section>
      <h1>Nabídka aut</h1>
      <div className="filters">
        {selectFilter('category', 'Kategorie')}
        {selectFilter('transmission', 'Převodovka')}
        {selectFilter('fuel_type', 'Palivo')}
        <label>
          Pobočka
          <select value={filters.branch_id} onChange={set('branch_id')}>
            <option value="">Vše</option>
            {branches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Cena/den od
          <input type="number" min={0} value={filters.min_price} onChange={set('min_price')} />
        </label>
        <label>
          Cena/den do
          <input type="number" min={0} value={filters.max_price} onChange={set('max_price')} />
        </label>
        <button className="secondary" onClick={() => setFilters(EMPTY_FILTERS)}>
          Zrušit filtry
        </button>
      </div>

      {success && <Message kind="success">{success}</Message>}
      {error && <Message kind="error">{error}</Message>}
      {cars && cars.length === 0 && <Message kind="info">Žádná auta neodpovídají zvoleným filtrům.</Message>}

      <div className="car-grid">
        {(cars ?? []).map((car) => (
          <article key={car.id} className="car-card">
            <CarImage src={car.image_url} label={`${car.brand} ${car.model}`} />
            <div className="car-body">
              <h3>
                {car.brand} {car.model} <span className="muted">({car.year})</span>
              </h3>
              <div className="muted small">{car.branch.name}</div>
              <div className="specs">
                <span>{carLabel(car.category)}</span>
                <span>{carLabel(car.transmission)}</span>
                <span>{carLabel(car.fuel_type)}</span>
                <span>{car.seats} míst</span>
              </div>
              {car.description && <p className="small">{car.description}</p>}
              <div className="prices">
                <strong>{formatPrice(car.daily_price)}</strong> / den ·{' '}
                <strong>{formatPrice(car.hourly_price)}</strong> / hod
              </div>
              {user?.role !== 'ADMIN' && <button onClick={() => reserve(car)}>Rezervovat</button>}
            </div>
          </article>
        ))}
      </div>

      {reserving && <ReservationForm car={reserving} onClose={() => setReserving(null)} onCreated={onCreated} />}
    </section>
  );
}
