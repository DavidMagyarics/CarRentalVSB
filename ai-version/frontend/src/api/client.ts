// HTTP/JSON client for the FastAPI backend (container diagram: SPA --> REST API, fetch).

export const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';

export type Role = 'CUSTOMER' | 'ADMIN';
export type PaymentMethod = 'CASH' | 'CARD';
export type ReservationStatus = 'DRAFT' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED';

export interface User {
  id: number;
  name: string;
  email: string;
  role: Role;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Branch {
  id: number;
  name: string;
  address: string;
}

export interface CarData {
  brand: string;
  model: string;
  year: number;
  license_plate: string;
  daily_price: number;
  hourly_price: number;
  category: string;
  transmission: string;
  fuel_type: string;
  seats: number;
  description: string;
  image_url: string;
  branch_id: number;
}

export interface Car extends CarData {
  id: number;
  branch: Branch;
}

export interface CarFilters {
  category?: string;
  transmission?: string;
  fuel_type?: string;
  min_price?: string;
  max_price?: string;
  branch_id?: string;
}

export interface Reservation {
  id: number;
  car_id: number;
  user_id: number;
  status: ReservationStatus;
  start_date: string;
  end_date: string;
  total_price: number;
  payment_method: PaymentMethod;
  created_at: string;
  rental_started: boolean;
  car: { id: number; brand: string; model: string; license_plate: string; image_url: string; branch_id: number };
  user: User;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

const TOKEN_KEY = 'carrental.token';

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable - the session just won't survive a reload */
  }
}

function errorMessage(status: number, body: unknown): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      // FastAPI / pydantic validation errors (422)
      return detail
        .map((d) => {
          const item = d as { loc?: unknown[]; msg?: string };
          const field = item.loc ? String(item.loc[item.loc.length - 1]) : '';
          return field ? `${field}: ${item.msg}` : item.msg;
        })
        .join('; ');
    }
  }
  return `Chyba serveru (${status})`;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, 'Server není dostupný. Běží backend?');
  }
  if (response.status === 204) return undefined as T;
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, errorMessage(response.status, data));
  return data as T;
}

function query(params: Record<string, string | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') search.set(key, value);
  }
  const text = search.toString();
  return text ? `?${text}` : '';
}

export const api = {
  // AuthService
  register: (name: string, email: string, password: string) =>
    request<TokenResponse>('POST', '/auth/register', { name, email, password }),
  login: (email: string, password: string) =>
    request<TokenResponse>('POST', '/auth/login', { email, password }),
  me: () => request<User>('GET', '/auth/me'),

  // FleetService
  branches: () => request<Branch[]>('GET', '/branches/'),
  cars: (filters: CarFilters = {}) => request<Car[]>('GET', `/cars/${query({ ...filters })}`),
  createCar: (data: CarData) => request<Car>('POST', '/cars/', data),
  updateCar: (id: number, data: Partial<CarData>) => request<Car>('PUT', `/cars/${id}`, data),
  deleteCar: (id: number) => request<void>('DELETE', `/cars/${id}`),

  // ReservationService
  availability: (carId: number, start: string, end: string) =>
    request<{ available: boolean }>(
      'GET',
      `/cars/${carId}/availability${query({ start_date: start, end_date: end })}`,
    ),
  createReservation: (carId: number, start: string, end: string, payment: PaymentMethod) =>
    request<Reservation>('POST', '/reservations/', {
      car_id: carId,
      start_date: start,
      end_date: end,
      payment_method: payment,
    }),
  myReservations: () => request<Reservation[]>('GET', '/reservations/me'),
  allReservations: () => request<Reservation[]>('GET', '/reservations/'),
  confirmReservation: (id: number) => request<Reservation>('POST', `/reservations/${id}/confirm`),
  cancelReservation: (id: number) => request<Reservation>('POST', `/reservations/${id}/cancel`),
  completeReservation: (id: number) => request<Reservation>('POST', `/reservations/${id}/complete`),
};
