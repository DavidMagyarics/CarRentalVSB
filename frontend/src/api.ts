export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type CarCategory = 'SEDAN' | 'SUV' | 'HATCHBACK' | 'VAN' | 'SPORTS'
export type Transmission = 'MANUAL' | 'AUTOMATIC'
export type FuelType = 'PETROL' | 'DIESEL' | 'ELECTRIC' | 'HYBRID'
export type UserRole = 'CUSTOMER' | 'ADMIN'
export type ReservationStatus = 'DRAFT' | 'CONFIRMED' | 'CANCELLED'
export type PaymentMethod = 'CASH' | 'CARD'

export interface Branch {
  id: number
  name: string
  address: string
}

export interface Car {
  id: number
  brand: string
  model: string
  year: number
  license_plate: string
  daily_price: number
  hourly_price: number
  category: CarCategory
  transmission: Transmission
  fuel_type: FuelType
  seats: number
  description: string | null
  image_url: string | null
  branch_id: number
  branch: Branch
}

export interface CarInput {
  brand: string
  model: string
  year: number
  license_plate: string
  daily_price: number
  hourly_price: number
  category: CarCategory
  transmission: Transmission
  fuel_type: FuelType
  seats: number
  description?: string | null
  image_url?: string | null
  branch_id: number
}

export interface CarFilters {
  category?: CarCategory | ''
  transmission?: Transmission | ''
  fuel_type?: FuelType | ''
  min_price?: number
  max_price?: number
  min_seats?: number
  branch_id?: number | ''
}

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
}

export interface AuthResult {
  access_token: string
  token_type: string
  user: User
}

export interface ReservationInput {
  car_id: number
  start_date: string
  end_date: string
  payment_method: PaymentMethod
}

export interface Reservation {
  id: number
  car_id: number
  user_id: number
  status: ReservationStatus
  start_date: string
  end_date: string
  total_price: number
  payment_method: PaymentMethod
  created_at: string
  car: Car
  user: User
}

export interface Availability {
  car_id: number
  start_date: string
  end_date: string
  available: boolean
}

const TOKEN_KEY = 'carrentalvsb_token'

export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function storeToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {
    // localStorage unavailable (private mode, blocked storage) — token just
    // won't survive a reload; the rest of the app still works this session.
  }
}

export function clearStoredToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {
    // see storeToken
  }
}

function authHeaders(token: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {}
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

async function handleVoidResponse(response: Response): Promise<void> {
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    throw new Error(
      typeof detail === 'string' ? detail : `Chyba serveru (${response.status})`,
    )
  }
}

export async function fetchBranches(): Promise<Branch[]> {
  const response = await fetch(`${API_BASE_URL}/branches/`)
  return handleResponse<Branch[]>(response)
}

export async function fetchCars(filters: CarFilters = {}): Promise<Car[]> {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      params.set(key, String(value))
    }
  })
  const qs = params.toString()
  const response = await fetch(`${API_BASE_URL}/cars/${qs ? `?${qs}` : ''}`)
  return handleResponse<Car[]>(response)
}

export async function createCar(token: string, input: CarInput): Promise<Car> {
  const response = await fetch(`${API_BASE_URL}/cars/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(input),
  })
  return handleResponse<Car>(response)
}

export async function updateCar(
  token: string,
  id: number,
  input: Partial<CarInput>,
): Promise<Car> {
  const response = await fetch(`${API_BASE_URL}/cars/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(input),
  })
  return handleResponse<Car>(response)
}

export async function deleteCar(token: string, id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/cars/${id}`, {
    method: 'DELETE',
    headers: { ...authHeaders(token) },
  })
  return handleVoidResponse(response)
}

export async function checkAvailability(
  carId: number,
  startDate: string,
  endDate: string,
): Promise<Availability> {
  const params = new URLSearchParams({ start_date: startDate, end_date: endDate })
  const response = await fetch(`${API_BASE_URL}/cars/${carId}/availability?${params}`)
  return handleResponse<Availability>(response)
}

export async function registerUser(
  name: string,
  email: string,
  password: string,
): Promise<AuthResult> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  })
  return handleResponse<AuthResult>(response)
}

export async function loginUser(email: string, password: string): Promise<AuthResult> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  return handleResponse<AuthResult>(response)
}

export async function fetchMe(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: authHeaders(token),
  })
  return handleResponse<User>(response)
}

export async function createReservation(
  token: string,
  input: ReservationInput,
): Promise<Reservation> {
  const response = await fetch(`${API_BASE_URL}/reservations/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(input),
  })
  return handleResponse<Reservation>(response)
}

export async function fetchMyReservations(token: string): Promise<Reservation[]> {
  const response = await fetch(`${API_BASE_URL}/reservations/me`, {
    headers: authHeaders(token),
  })
  return handleResponse<Reservation[]>(response)
}

export async function fetchAllReservations(token: string): Promise<Reservation[]> {
  const response = await fetch(`${API_BASE_URL}/reservations/`, {
    headers: authHeaders(token),
  })
  return handleResponse<Reservation[]>(response)
}

export async function confirmReservation(token: string, id: number): Promise<Reservation> {
  const response = await fetch(`${API_BASE_URL}/reservations/${id}/confirm`, {
    method: 'POST',
    headers: authHeaders(token),
  })
  return handleResponse<Reservation>(response)
}

export async function cancelReservation(token: string, id: number): Promise<Reservation> {
  const response = await fetch(`${API_BASE_URL}/reservations/${id}/cancel`, {
    method: 'POST',
    headers: authHeaders(token),
  })
  return handleResponse<Reservation>(response)
}
