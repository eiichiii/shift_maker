import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/schedules': 'http://localhost:8001',
      '/shift-requests': 'http://localhost:8001',
      '/members': 'http://localhost:8001',
      '/availabilities': 'http://localhost:8001',
      '/shift-generation': 'http://localhost:8001'
    }
  }
})
