import type { Car } from '../api'
import { CATEGORY_LABELS, FUEL_LABELS, TRANSMISSION_LABELS } from '../constants'
import CarIllustration from './CarIllustration'

interface Props {
  car: Car
  onReserve: (car: Car) => void
}

export default function CarCard({ car, onReserve }: Props) {
  return (
    <article className={`car-card car-art-${car.category.toLowerCase()}`}>
      <div className="car-card-art">
        <CarIllustration category={car.category} className="car-card-illustration" />
        <span className="car-card-badge">{CATEGORY_LABELS[car.category]}</span>
      </div>

      <div className="car-card-body">
        <h3>
          {car.brand} {car.model}
        </h3>
        <p className="car-card-meta">
          {car.year} · {car.license_plate}
        </p>

        {car.description && <p className="car-card-desc">{car.description}</p>}

        <ul className="car-card-specs">
          <li>{TRANSMISSION_LABELS[car.transmission]}</li>
          <li>{FUEL_LABELS[car.fuel_type]}</li>
          <li>{car.seats} míst</li>
        </ul>

        <div className="car-card-footer">
          <div className="car-card-price">
            <strong>{car.daily_price.toLocaleString('cs-CZ')} Kč</strong>
            <span> / den</span>
          </div>
          <button type="button" onClick={() => onReserve(car)}>
            Rezervovat
          </button>
        </div>
      </div>
    </article>
  )
}
