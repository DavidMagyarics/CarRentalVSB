import type { Car } from '../api'

interface Props {
  cars: Car[]
  onReserve: (car: Car) => void
}

export default function CarList({ cars, onReserve }: Props) {
  if (cars.length === 0) {
    return <p>Momentálně nejsou k dispozici žádná auta.</p>
  }

  return (
    <ul className="car-list">
      {cars.map((car) => (
        <li key={car.id} className="car-card">
          <div>
            <strong>
              {car.brand} {car.model}
            </strong>{' '}
            ({car.year})
            <div className="plate">{car.license_plate}</div>
          </div>
          <div className="price">{car.daily_price} Kč / den</div>
          <button type="button" onClick={() => onReserve(car)}>
            Rezervovat
          </button>
        </li>
      ))}
    </ul>
  )
}
