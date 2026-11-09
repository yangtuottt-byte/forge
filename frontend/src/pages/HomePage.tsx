// 临时占位首页(Task 5 将替换为 Dashboard 业务页)
export function HomePage() {
  return (
    <div className="mx-auto max-w-2xl rounded-xl border border-slate-800 bg-slate-900/40 p-8 text-center">
      <h1 className="text-2xl font-semibold">Forge · 多智能体协作研发平台</h1>
      <p className="mt-2 text-sm text-slate-400">
        前端骨架就绪。Vite + React + TypeScript + Tailwind + Vitest + ESLint 已联调。
      </p>
      <p className="mt-4 font-mono text-xs text-slate-500">
        .env → VITE_API_URL · 后端 CORS · WebSocket 实时进度
      </p>
    </div>
  )
}
