import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const frontendInternalApiKey =
    env.FRONTEND_INTERNAL_API_KEY ?? '123-frontend-proxy-456'

  return {
    plugins: [react()],
    server: {
      host: '127.0.0.1',
      port: 5173,
      proxy: {
        '/ui-api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/ui-api/, '/api'),
          headers: {
            'X-Frontend-Proxy-Key': frontendInternalApiKey,
          },
        },
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
