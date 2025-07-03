import path from "node:path"
import { TanStackRouterVite } from "@tanstack/router-vite-plugin"
import react from "@vitejs/plugin-react-swc"
import { defineConfig, loadEnv } from "vite"

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Cargar variables de entorno
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    plugins: [react(), TanStackRouterVite()],
    
    // Configuración del servidor de desarrollo
    server: {
      port: 5173,
      host: true,
      open: false,
    },
    
    // Variables de entorno que se exponen al cliente
    define: {
      // Asegurar que estas variables estén disponibles
      __VITE_CLERK_PUBLISHABLE_KEY__: JSON.stringify(env.VITE_CLERK_PUBLISHABLE_KEY || process.env.VITE_CLERK_PUBLISHABLE_KEY),
      __VITE_API_URL__: JSON.stringify(env.VITE_API_URL || process.env.VITE_API_URL || 'http://localhost:8000'),
    },
    
    // Configuración de build
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
  }
})
