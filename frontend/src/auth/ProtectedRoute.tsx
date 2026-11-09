import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './useAuth'

// 路由守卫:无 token 跳 /login,有 token 渲染 <Outlet />(受保护子路由)
export function ProtectedRoute() {
  const { token } = useAuth()
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return <Outlet />
}
