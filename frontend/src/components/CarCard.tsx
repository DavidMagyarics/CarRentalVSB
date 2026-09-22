import { useState } from 'react'
import type { Car } from '../api'
import { CATEGORY_LABELS, FUEL_LABELS, TRANSMISSION_LABELS } from '../constants'
import CarIllustration from './CarIllustration'

interface Props {
  car: Car
  onReserve: (car: Car) => void
}

export default function CarCard({ car, onReserve }: Props) {
  const [photoFailed, setPhotoFailed] = useState(false)
  const showPhoto = Boolean(car.image_url) && !photoFailed

  return (
    <article className={`car-card car-art-${car.category.toLowerCase()}`}>
      <div className={`car-card-art${showPhoto ? ' car-card-art-photo' : ''}`}>
        {showPhoto ? (
          <img
            src={car.image_url ?? undefined}
            alt={`${car.brand} ${car.model}`}
            className="car-card-photo"
            loading="lazy"
            onError={() => setPhotoFailed(true)}
          />
        ) : (
          <CarIllustration category={car.category} className="car-card-illustration" />
        )}
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
            <div className="car-card-price-daily">
              <strong>{car.daily_price.toLocaleString('cs-CZ')} Kč</strong>
              <span> / den</span>
            </div>
            <div className="car-card-price-hourly">
              {car.hourly_price.toLocaleString('cs-CZ')} Kč / h
            </div>
          </div>
          <button type="button" onClick={() => onReserve(car)}>
            Rezervovat
          </button>
        </div>
      </div>
    </article>
  )
}
