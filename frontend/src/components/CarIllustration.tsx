import type { CarCategory } from '../api'

interface CarShape {
  body: string
  window: string
  wheelY: number
  wheelR: number
  wheelX: [number, number]
}

const SHAPES: Record<CarCategory, CarShape> = {
  SEDAN: {
    body: 'M16,80 L16,72 Q16,66 22,64 L56,64 L74,38 Q78,30 88,30 L152,30 Q162,30 166,38 L184,64 L218,64 Q224,66 224,72 L224,80 Z',
    window: 'M92,38 L106,34 L148,34 L162,38 L162,60 L92,60 Z',
    wheelY: 80,
    wheelR: 14,
    wheelX: [62, 178],
  },
  HATCHBACK: {
    body: 'M16,80 L16,72 Q16,66 22,64 L52,64 L70,36 Q74,28 84,28 L136,28 Q145,28 149,35 L158,64 L206,64 Q212,66 212,72 L212,80 Z',
    window: 'M84,35 L98,31 L134,31 L152,60 L84,60 Z',
    wheelY: 80,
    wheelR: 14,
    wheelX: [58, 168],
  },
  SUV: {
    body: 'M14,80 L14,68 Q14,60 22,58 L48,58 L64,26 Q68,18 78,18 L158,18 Q168,18 172,26 L188,58 L212,58 Q220,60 220,68 L220,80 Z',
    window: 'M80,26 L96,21 L156,21 L172,58 L80,58 Z',
    wheelY: 80,
    wheelR: 16,
    wheelX: [60, 180],
  },
  VAN: {
    body: 'M12,80 L12,54 Q12,22 40,22 L206,22 Q224,22 224,54 L224,80 Z',
    window: 'M40,29 L108,29 L108,58 L40,58 Z M118,29 L196,29 L196,58 L118,58 Z',
    wheelY: 80,
    wheelR: 15,
    wheelX: [56, 184],
  },
  SPORTS: {
    body: 'M14,80 L14,74 Q14,68 22,67 L46,64 L78,34 Q84,27 94,26 L148,26 Q160,26 168,36 L192,66 L208,67 Q220,68 220,74 L220,80 Z',
    window: 'M92,36 L112,28 L150,28 L176,54 L100,60 Z',
    wheelY: 80,
    wheelR: 15,
    wheelX: [54, 180],
  },
}

interface Props {
  category: CarCategory
  className?: string
}

export default function CarIllustration({ category, className }: Props) {
  const shape = SHAPES[category]

  return (
    <svg viewBox="0 0 240 100" className={className} role="img" aria-label={category}>
      <ellipse className="car-illustration-shadow" cx="120" cy="90" rx="100" ry="6" />
      <path className="car-illustration-body" d={shape.body} />
      <path className="car-illustration-window" d={shape.window} />
      {shape.wheelX.map((wx) => (
        <g key={wx}>
          <circle
            className="car-illustration-wheel"
            cx={wx}
            cy={shape.wheelY}
            r={shape.wheelR}
          />
          <circle
            className="car-illustration-hub"
            cx={wx}
            cy={shape.wheelY}
            r={shape.wheelR - 6}
          />
        </g>
      ))}
    </svg>
  )
}
