import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// dev 时把 /api 转发到本地 FastAPI，前端无需关心跨域
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
