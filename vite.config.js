import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: { // Add this 'server' configuration block
    proxy: {
      '/api': { // Any request starting with /api will be proxied
        target: 'http://localhost:5001', // Your Flask backend address and port
        changeOrigin: true, // Recommended for most proxy setups
        // No rewrite rule needed here because your Flask app's route
        // (/api/upload-and-generate) already includes the /api prefix.
      }
    }
  }
})