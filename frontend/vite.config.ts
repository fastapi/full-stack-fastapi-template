import { TanStackRouterVite } from "@tanstack/router-vite-plugin";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react(), TanStackRouterVite()],
	server: {
		watch: {
			usePolling: true,
		},
		host: "0.0.0.0", // Allows access from the container
		port: 5173, // Matches the mapped port in Docker Compose
		strictPort: true,
	},
});
