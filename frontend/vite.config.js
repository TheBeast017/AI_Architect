import { defineConfig } from "vite";

export default defineConfig({
  base: "/",
  build: {
    outDir: "../src/engagent/api/static",
    emptyOutDir: true,
  },
  server: {
    proxy: { "/design": "http://127.0.0.1:8000", "/health": "http://127.0.0.1:8000" },
  },
});