// 前端 API 基础 URL。
// - dev: 前端 Vite(5173)直连后端(8000),后端 CORS 已放行 5173。
// - prod: 经 nginx 同源反代,设 /api/v1(Dockerfile 已 --build-arg 注入);
//   用 || 使空字符串也回退到默认 dev 值(?? 只挡 null/undefined,会放过空串)
export const API_BASE: string =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// WebSocket 基础地址:http(s):// → ws(s)://,便于运行时构造 WS URL(Task 5 实时进度用)
export function toWsBase(url: string): string {
  return url.replace(/^http/i, 'ws')
}
