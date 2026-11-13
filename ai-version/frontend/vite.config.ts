import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Deployment diagram: the SPA is served on port 5173.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  preview: { port: 5173 },
});
