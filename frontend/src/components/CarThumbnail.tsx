import { useState } from 'react'
import type { Car } from '../api'
import CarIllustration from './CarIllustration'

interface Props {
  car: Pick<Car, 'image_url' | 'category' | 'brand' | 'model'>
}

export default function CarThumbnail({ car }: Props) {
  const [photoFailed, setPhotoFailed] = useState(false)
  const showPhoto = Boolean(car.image_url) && !photoFailed

  return (
    <div className="car-thumbnail">
      {showPhoto ? (
        <img
          src={car.image_url ?? undefined}
          alt={`${car.brand} ${car.model}`}
          loading="lazy"
          onError={() => setPhotoFailed(true)}
        />
      ) : (
        <CarIllustration category={car.category} />
      )}
    </div>
  )
}
