import { useContext } from 'react'
import { AuthContext } from './context'

// 用在组件内读取认证状态。须被 <AuthProvider> 包裹。
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth 必须在 <AuthProvider> 内使用')
  return ctx
}
