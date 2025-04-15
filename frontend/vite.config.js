import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/',
  plugins: [react()],
  preview: {
    port: 4173,
    strictPort: true,
    // ✅ This is the fix 👇
    allowedHosts: ['ecfr-nu4s.onrender.com']
  }
});