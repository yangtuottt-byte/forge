import { createContext } from 'react'
import type { UserOut } from '../api/types'

// 认证上下文值:token + user + loading + 登录/注册/登出
// token 持久化 localStorage,user 内存态(见 AuthProvider)
export interface AuthContextValue {
  token: string | null
  user: UserOut | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
