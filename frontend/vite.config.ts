/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    // e2e/ holds Playwright specs (a different test runner, with its own
    // `test`/`expect` and browser fixtures) — Vitest must not try to
    // collect them too.
    exclude: ['e2e/**', 'node_modules/**'],
  },
})
