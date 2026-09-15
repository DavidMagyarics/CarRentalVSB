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

export interface Reservation extends ReservationInput {
  id: number
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
