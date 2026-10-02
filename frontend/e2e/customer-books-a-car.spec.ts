import { expect, test } from '@playwright/test'

// The main end-to-end scenario (see roadmap.md, Week 6): a brand-new
// customer registers, picks a car, fills in valid pickup/return dates, pays
// by cash, submits, and sees the reservation waiting for admin approval
// under "Moje rezervace". Runs against a real backend + frontend (see
// playwright.config.ts) and the actual carrental.db — not a mocked API —
// so it only ever creates new rows (a new customer, a new DRAFT
// reservation) and never touches anything another run created.

function nextMondayAt(hour: number): Date {
  // A Monday comfortably in the future, so a same-length pickup->return
  // span (e.g. +1 day, landing on Tuesday) is *also* guaranteed to be a
  // weekday under the Mon-Fri opening-hours rule, regardless of which day
  // this test happens to run on. (Picking "today + N days" without this and
  // deriving the return date from it can silently land the return on a
  // Saturday — exactly the kind of off-by-one this feature exists to catch.)
  const date = new Date()
  date.setDate(date.getDate() + 14)
  const daysUntilMonday = (8 - date.getDay()) % 7
  date.setDate(date.getDate() + daysUntilMonday)
  date.setHours(hour, 0, 0, 0)
  return date
}

function toDatetimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

test('customer registers, books a car, and sees it awaiting approval', async ({ page }) => {
  const uniqueEmail = `e2e-${Date.now()}@example.com`

  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Najdi si auto na míru' })).toBeVisible()

  // Reserve while logged out -> the app asks to log in / register first.
  const firstCarCard = page.locator('.car-card').first()
  await expect(firstCarCard).toBeVisible()
  const carTitle = await firstCarCard.locator('h3').innerText()
  await firstCarCard.getByRole('button', { name: 'Rezervovat' }).click()

  await expect(page.getByText('Pro rezervaci auta se prosím přihlas nebo si vytvoř účet.')).toBeVisible()
  await page.locator('.auth-tabs button', { hasText: 'Vytvořit účet' }).click()

  await page.getByLabel('Jméno').fill('E2E Test Customer')
  await page.getByLabel('E-mail').fill(uniqueEmail)
  await page.getByLabel('Heslo').fill('heslo123')
  await page.locator('form button[type="submit"]').click()

  // Registering auto-opens the booking form for the car that was clicked.
  await expect(page.getByRole('heading', { name: `Rezervace: ${carTitle}` })).toBeVisible()

  const pickup = nextMondayAt(9)
  const dropoff = new Date(pickup.getTime() + 24 * 60 * 60 * 1000)

  await page.getByLabel('Vyzvednutí').fill(toDatetimeLocal(pickup))
  await page.getByLabel('Vrácení').fill(toDatetimeLocal(dropoff))

  await expect(page.getByText('Termín je dostupný')).toBeVisible()

  // Payment method defaults to Cash ("Hotově") — no extra click needed.
  await page.getByRole('button', { name: 'Potvrdit rezervaci' }).click()

  await expect(page.getByText('Rezervace byla úspěšně vytvořena.')).toBeVisible()

  await page.getByRole('button', { name: 'Moje rezervace' }).click()
  const reservationCard = page.locator('.reservation-card', { hasText: carTitle })
  await expect(reservationCard).toBeVisible()
  await expect(reservationCard.getByText('Čeká na schválení administrátorem')).toBeVisible()
})
