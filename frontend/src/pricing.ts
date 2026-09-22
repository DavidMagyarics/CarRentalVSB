/**
 * Mirrors backend/app/crud.py::calculate_price exactly, so the live price
 * shown while picking dates matches what the server will actually charge.
 * The server always recomputes and stores the authoritative total_price —
 * this is only for instant UI feedback.
 */
export function calculatePrice(dailyPrice: number, hourlyPrice: number, start: Date, end: Date): number {
  const totalHours = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60))
  if (totalHours <= 0) return 0
  const fullDays = Math.floor(totalHours / 24)
  const remainingHours = totalHours - fullDays * 24
  const remainingPrice = remainingHours > 0 ? Math.min(remainingHours * hourlyPrice, dailyPrice) : 0
  return fullDays * dailyPrice + remainingPrice
}

export function formatDuration(start: Date, end: Date): string {
  const totalMinutes = Math.round((end.getTime() - start.getTime()) / (1000 * 60))
  if (totalMinutes <= 0) return ''
  const days = Math.floor(totalMinutes / (60 * 24))
  const hours = Math.floor((totalMinutes % (60 * 24)) / 60)
  const parts: string[] = []
  if (days > 0) parts.push(`${days} ${days === 1 ? 'den' : days < 5 ? 'dny' : 'dní'}`)
  if (hours > 0) parts.push(`${hours} ${hours === 1 ? 'hodina' : hours < 5 ? 'hodiny' : 'hodin'}`)
  return parts.join(' ') || 'méně než hodina'
}
