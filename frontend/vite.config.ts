import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite 配置:前端开发服务器
// dev: vite (5173) → 经后端 CORS 直连后端 api (8000)
// prod: 经 nginx 同源反代,Vite 只负责构建产物
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // 允许局域网访问(docker/容器调试)
  },
})
