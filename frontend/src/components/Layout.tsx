import { Outlet } from 'react-router-dom'
import { Hammer } from 'lucide-react'

// 全局布局:顶部导航 + 内容区。受保护路由包裹其下。
export function Layout() {
  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-2 px-6 py-4">
          <Hammer className="h-5 w-5 text-indigo-400" />
          <span className="text-lg font-semibold tracking-tight">Forge</span>
          <span className="ml-1 rounded bg-slate-800 px-1.5 py-0.5 text-xs text-slate-400">
            多智能体协作研发平台
          </span>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
