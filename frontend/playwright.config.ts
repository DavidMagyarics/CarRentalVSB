import { defineConfig, devices } from '@playwright/test'

// E2E tests drive the real app end to end: a real backend (uvicorn) and a
// real frontend dev server, both started fresh for the test run and torn
// down afterwards. They use the project's normal dev ports (8000/5173, see
// README.md) since the CORS origin allowed by the backend is hardcoded to
// http://localhost:5173 (backend/app/main.py) — running on other ports
// would need a CORS change just for testing. Don't run this while your own
// `uvicorn`/`npm run dev` are already using those ports.
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command:
        process.platform === 'win32'
          ? '..\\backend\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8000'
          : '../backend/.venv/bin/python -m uvicorn app.main:app --port 8000',
      cwd: '../backend',
      url: 'http://localhost:8000/cars/',
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: 'npm run dev -- --port 5173 --strictPort',
      url: 'http://localhost:5173',
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
})
