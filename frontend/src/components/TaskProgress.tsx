import { CheckCircle2, Clock, Loader2, XCircle } from 'lucide-react'
import type { TaskStatus } from '../api/types'
import { cn } from '../lib/cn'

interface TaskProgressProps {
  status: TaskStatus
  progress: number // 0-100
}

const STATUS_META = {
  pending: { label: '排队中', Icon: Clock, text: 'text-slate-400' },
  running: { label: '执行中', Icon: Loader2, text: 'text-indigo-400' },
  done: { label: '已完成', Icon: CheckCircle2, text: 'text-emerald-400' },
  failed: { label: '失败', Icon: XCircle, text: 'text-rose-400' },
} as const

const BAR_CLS: Record<TaskStatus, string> = {
  pending: 'bg-slate-500',
  running: 'bg-indigo-500',
  done: 'bg-emerald-500',
  failed: 'bg-rose-500',
}

// 进度条 + 状态徽标:running 时图标旋转
export function TaskProgress({ status, progress }: TaskProgressProps) {
  const meta = STATUS_META[status]
  const { Icon } = meta
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5">
      <div className="mb-3 flex items-center gap-2 text-sm">
        <Icon
          className={cn(
            'h-4 w-4',
            meta.text,
            status === 'running' && 'animate-spin',
          )}
        />
        <span className="font-medium">{meta.label}</span>
        <span className="font-mono text-xs text-slate-500">{status}</span>
        <span className="ml-auto font-mono text-xs text-slate-400">
          {progress}%
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            BAR_CLS[status],
          )}
          style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
        />
      </div>
    </div>
  )
}
