import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { getMe, login as loginApi, register as registerApi } from '../api/auth'
import { getToken, setToken } from '../api/client'
import type { UserOut } from '../api/types'
import { AuthContext, type AuthContextValue } from './context'

// 认证提供者:仅导出组件(不混 hook 导出,避免 fast-refresh 失效)
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => getToken())
  const [user, setUser] = useState<UserOut | null>(null)
  const [loading, setLoading] = useState(false)
  const restored = useRef(false) // 守卫:只恢复一次,不随 token 变化重跑

  // 挂载时:若已有 token,拉 /auth/me 恢复用户(刷新页面后保持登录态)
  useEffect(() => {
    if (restored.current) return
    restored.current = true
    if (!token) return
    let cancelled = false
    setLoading(true)
    getMe()
      .then((u) => {
        if (!cancelled) setUser(u)
      })
      .catch(() => {
        // token 失效或用户不存在 → 清登录
        setToken(null)
        setTokenState(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [token])

  const login = useCallback(async (email: string, password: string) => {
    const t = await loginApi(email, password)
    setToken(t.access_token)
    setTokenState(t.access_token)
    const u = await getMe()
    setUser(u)
  }, [])

  const register = useCallback(async (email: string, password: string) => {
    const t = await registerApi(email, password)
    setToken(t.access_token)
    setTokenState(t.access_token)
    const u = await getMe()
    setUser(u)
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setTokenState(null)
    setUser(null)
  }, [])

  const value: AuthContextValue = { token, user, loading, login, register, logout }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
