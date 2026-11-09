import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Vitest 配置:jsdom 环境 + React 插件
// 仅测试用,不参与生产构建
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
})
