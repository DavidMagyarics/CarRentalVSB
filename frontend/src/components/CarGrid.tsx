import type { Car } from '../api'
import CarCard from './CarCard'

interface Props {
  cars: Car[]
  onReserve: (car: Car) => void
}

export default function CarGrid({ cars, onReserve }: Props) {
  if (cars.length === 0) {
    return <p className="empty-state">Žádná auta neodpovídají zvoleným filtrům.</p>
  }

  return (
    <div className="car-grid">
      {cars.map((car) => (
        <CarCard key={car.id} car={car} onReserve={onReserve} />
      ))}
    </div>
  )
}
