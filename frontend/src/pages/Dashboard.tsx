import { useState, type FormEvent } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { createTask, getTask } from '../api/tasks'
import { TaskProgress } from '../components/TaskProgress'
import { TaskResult } from '../components/TaskResult'
import { Button } from '../components/Button'
import { useTaskProgress } from '../realtime/useTaskProgress'

// 示例任务目标:点击填入
const EXAMPLES = [
  '编写 Python 斐波那契数列函数',
  '写一个 SQLite 待办事项 API',
  '实现链表反转并补测试',
]

// 核心页:提交任务 → WS 实时进度 → 交付结果
export function Dashboard() {
  const [goal, setGoal] = useState(EXAMPLES[0])
  const [activeId, setActiveId] = useState<number | null>(null)
  const [error, setError] = useState('')

  // 提交任务:POST /tasks?goal=...(react-query mutation)
  const submit = useMutation({
    mutationFn: createTask,
    onMutate: () => setError(''),
    onSuccess: (d) => {
      setActiveId(d.id)
      setError('')
    },
    onError: (e) => setError(e instanceof Error ? e.message : '提交失败'),
  })

  // WebSocket 实时进度(独立 hook,不受 react-query 管理)
  const { status, progress } = useTaskProgress(activeId)

  // 完成后经 react-query 拉取结果(缓存 / 重试 / 去重)
  const finishQuery = useQuery({
    queryKey: ['task', activeId],
    queryFn: () => getTask(activeId!),
    enabled: activeId != null && status === 'done',
  })
  const result = finishQuery.data?.result ?? ''

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!goal.trim()) {
      setError('请输入任务目标')
      return
    }
    submit.mutate(goal.trim())
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* 提交任务 */}
      <section className="rounded-xl border border-slate-800 bg-slate-900/40 p-6">
        <h1 className="text-lg font-semibold">提交研发任务</h1>
        <p className="mt-1 text-sm text-slate-400">
          多 Agent 将「规划 → 研究 → 执行 → 审查」协作完成,实时展示进度。
        </p>
        <form onSubmit={onSubmit} className="mt-4 space-y-3">
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="描述你的研发任务…"
            className="w-full min-h-[88px] rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <div className="flex flex-wrap items-center gap-2">
            {EXAMPLES.map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => setGoal(g)}
                className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-300 transition hover:bg-slate-800"
              >
                {g}
              </button>
            ))}
            <Button type="submit" loading={submit.isPending} className="ml-auto">
              提交任务
            </Button>
          </div>
        </form>
        {error ? <p className="mt-3 text-sm text-rose-400">{error}</p> : null}
      </section>

      {/* 当前任务进度 */}
      {activeId != null ? (
        <section className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">任务编号 #{activeId}</span>
            <button
              onClick={() => {
                setActiveId(null)
                setError('')
              }}
              className="text-indigo-400 hover:underline"
            >
              换个任务
            </button>
          </div>

          <TaskProgress status={status} progress={progress} />

          {status === 'done' ? <TaskResult result={result} /> : null}
          {status === 'failed' ? (
            <div className="rounded-xl border border-rose-800/60 bg-rose-950/30 p-4 text-sm text-rose-300">
              任务执行失败(已标记)。可点右上「换个任务」重新提交。
            </div>
          ) : null}
        </section>
      ) : (
        <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center text-sm text-slate-500">
          提交一个任务,启动多 Agent 协作。
        </div>
      )}
    </div>
  )
}
