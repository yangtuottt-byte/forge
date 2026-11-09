import { Outlet, useNavigate } from 'react-router-dom'
import { Hammer } from 'lucide-react'
import { useAuth } from '../auth/useAuth'
import { Button } from './Button'

// 全局布局:顶部导航(品牌 + 当前用户 + 退出)+ 内容区。受保护路由包裹其下。
export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const onLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <Hammer className="h-5 w-5 text-indigo-400" />
            <span className="text-lg font-semibold tracking-tight">Forge</span>
            <span className="ml-1 rounded bg-slate-800 px-1.5 py-0.5 text-xs text-slate-400">
              多智能体协作研发平台
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden max-w-[200px] truncate text-sm text-slate-300 sm:inline">
              {user?.email}
            </span>
            <Button variant="ghost" className="h-8 px-3 text-xs" onClick={onLogout}>
              退出
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
