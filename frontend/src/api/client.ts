import { API_BASE } from '../lib/apiBase'

export const TOKEN_KEY = 'forge_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

// HTTP 错误:携带状态码 + 解析出的错误信息(后端 detail 字段)
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function readError(res: Response): Promise<string> {
  try {
    const data: unknown = await res.json()
    if (data && typeof data === 'object') {
      const detail = (data as { detail?: unknown }).detail
      if (typeof detail === 'string') return detail
      return JSON.stringify(data)
    }
    return String(data)
  } catch {
    return `HTTP ${res.status}`
  }
}

// 统一请求封装:
// 1) 自动注入 Authorization 头(从 localStorage 取 token)
// 2) 自动处理 JSON(Content-Type + body 解析)
// 3) 401 → 清 token(交由 AuthContext / 路由守卫处理跳转)
// 4) 非 2xx → 抛 ApiError(含后端 detail)
export async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers = new Headers(opts.headers)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (opts.body && typeof opts.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers })

  if (res.status === 401) {
    setToken(null)
    throw new ApiError(401, '未登录或登录已过期,请重新登录')
  }
  if (!res.ok) {
    throw new ApiError(res.status, await readError(res))
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}
