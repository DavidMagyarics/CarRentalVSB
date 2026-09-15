export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface Car {
  id: number
  brand: string
  model: string
  year: number
  license_plate: string
  daily_price: number
}

export interface ReservationInput {
  car_id: number
  customer_name: string
  customer_email: string
  start_date: string
  end_date: string
}

export type ReservationStatus = 'DRAFT' | 'CONFIRMED' | 'CANCELLED'

export interface Reservation {
  id: number
  car_id: number
  user_id: number
  status: ReservationStatus
  start_date: string
  end_date: string
  created_at: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    throw new Error(
      typeof detail === 'string' ? detail : `Chyba serveru (${response.status})`,
    )
  }
  return response.json() as Promise<T>
}

export async function fetchCars(): Promise<Car[]> {
  const response = await fetch(`${API_BASE_URL}/cars/`)
  return handleResponse<Car[]>(response)
}

export async function createReservation(
  input: ReservationInput,
): Promise<Reservation> {
  const response = await fetch(`${API_BASE_URL}/reservations/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  return handleResponse<Reservation>(response)
}
