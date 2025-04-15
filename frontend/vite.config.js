import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/', // ✅ Required for correct route resolution on Render
  plugins: [react()],
  server: {
    port: 5173,
  },
});