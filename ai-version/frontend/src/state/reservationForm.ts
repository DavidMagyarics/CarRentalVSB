// ReservationForm state machine (state-reservation-form.puml) as a pure reducer.
//
//   Editing { Empty -> <dates> -> Invalid | Checking -> Available | Unavailable | Invalid }
//   Available --submit()--> Submitting --[409/422]--> Available (with error)
//                                      --[201]------> done (close the form)
//   Editing --cancel()--> closed

import type { PaymentMethod } from '../api/client';

export type FormPhase =
  | 'empty' // "No dates"            (availability: idle)
  | 'invalid' // "Invalid dates"     (availability: error)
  | 'checking' // "Checking availability"
  | 'available'
  | 'unavailable'
  | 'submitting'
  | 'done';

export interface FormState {
  phase: FormPhase;
  start: string; // datetime-local value, e.g. "2030-01-07T09:00"
  end: string;
  payment: PaymentMethod;
  estimate: number | null;
  error: string | null; // date error, check failure, or submit error
  checkId: number; // increases with every enter_dates - stale results are ignored
}

export type FormEvent =
  | { type: 'enter_dates'; start: string; end: string; now: Date; prices: [number, number] }
  | { type: 'check_result'; checkId: number; available: boolean }
  | { type: 'check_failed'; checkId: number; error: string }
  | { type: 'choose_payment'; method: PaymentMethod }
  | { type: 'submit' }
  | { type: 'submit_failed'; error: string }
  | { type: 'submit_succeeded' };

export const initialFormState: FormState = {
  phase: 'empty',
  start: '',
  end: '',
  payment: 'CASH',
  estimate: null,
  error: null,
  checkId: 0,
};

const OPEN_MINUTES = 8 * 60;
const CLOSE_MINUTES = 20 * 60;

function withinOpeningHours(d: Date): boolean {
  const day = d.getDay(); // 0 = Sunday
  if (day === 0 || day === 6) return false;
  const minutes = d.getHours() * 60 + d.getMinutes() + d.getSeconds() / 60;
  return minutes >= OPEN_MINUTES && minutes <= CLOSE_MINUTES;
}

/** check_dates(): Mon-Fri 08:00-20:00 and return after pickup. Returns an error or null. */
export function checkDates(start: string, end: string, now: Date): string | null {
  const s = new Date(start);
  const e = new Date(end);
  if (Number.isNaN(s.getTime()) || Number.isNaN(e.getTime())) return 'Zadejte termín vyzvednutí i vrácení.';
  if (e <= s) return 'Vrácení auta musí být později než jeho vyzvednutí.';
  if (!withinOpeningHours(s) || !withinOpeningHours(e))
    return 'Vyzvednutí i vrácení auta jsou možné jen v pracovní dny (Po–Pá) mezi 8:00 a 20:00.';
  if (s < now) return 'Termín vyzvednutí nesmí být v minulosti.';
  return null;
}

/** estimate_price(): daily rate per full 24 h + started hours, the rest capped at one day. */
export function estimatePrice(start: string, end: string, daily: number, hourly: number): number {
  const ms = new Date(end).getTime() - new Date(start).getTime();
  if (!(ms > 0)) return 0;
  const dayMs = 24 * 3600 * 1000;
  const fullDays = Math.floor(ms / dayMs);
  const restHours = Math.ceil((ms - fullDays * dayMs) / (3600 * 1000));
  const rest = restHours > 0 ? Math.min(restHours * hourly, daily) : 0;
  return Math.round((fullDays * daily + rest) * 100) / 100;
}

export function reservationFormReducer(state: FormState, event: FormEvent): FormState {
  switch (event.type) {
    case 'enter_dates': {
      if (state.phase === 'submitting' || state.phase === 'done') return state;
      const checkId = state.checkId + 1;
      const base = { ...state, start: event.start, end: event.end, checkId };
      if (!event.start || !event.end) return { ...base, phase: 'empty', estimate: null, error: null };
      const error = checkDates(event.start, event.end, event.now);
      if (error) return { ...base, phase: 'invalid', estimate: null, error };
      // entry / estimate_price()
      const [daily, hourly] = event.prices;
      return { ...base, phase: 'checking', estimate: estimatePrice(event.start, event.end, daily, hourly), error: null };
    }
    case 'check_result':
      if (state.phase !== 'checking' || event.checkId !== state.checkId) return state;
      return { ...state, phase: event.available ? 'available' : 'unavailable' };
    case 'check_failed':
      if (state.phase !== 'checking' || event.checkId !== state.checkId) return state;
      return { ...state, phase: 'invalid', error: event.error };
    case 'choose_payment':
      return state.phase === 'available' ? { ...state, payment: event.method } : state;
    case 'submit':
      // submit() is only possible from Available (disabled in Invalid / Unavailable).
      return state.phase === 'available' ? { ...state, phase: 'submitting', error: null } : state;
    case 'submit_failed':
      return state.phase === 'submitting' ? { ...state, phase: 'available', error: event.error } : state;
    case 'submit_succeeded':
      return state.phase === 'submitting' ? { ...state, phase: 'done' } : state;
    default:
      return state;
  }
}
