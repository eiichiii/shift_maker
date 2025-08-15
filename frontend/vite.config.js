import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    allowedHosts: 'all',
    proxy: {
      '/schedules': 'http://localhost:8000',
      '/shift-requests': 'http://localhost:8000',
      '/members': 'http://localhost:8000',
      '/availabilities': 'http://localhost:8000',
      '/shift-generation': 'http://localhost:8000'
    }
  }
})
