import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/',
  plugins: [react()],
  server: {
    host: true, // ✅ allows access from LAN IPs
    port: 5173,
  },
  preview: {
    port: 4173,
    strictPort: true,
    allowedHosts: ['ecfr-nu4s.onrender.com', 'localhost'], // Add others if needed
  }
});