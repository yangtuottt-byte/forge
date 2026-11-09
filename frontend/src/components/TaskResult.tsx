import { useState } from 'react'
import { Check, Copy, FileText } from 'lucide-react'

interface TaskResultProps {
  result: string
}

// 交付结果展示:等宽、可复制。结果为空时显示占位。
export function TaskResult({ result }: TaskResultProps) {
  const [copied, setCopied] = useState(false)

  if (!result) {
    return (
      <p className="rounded-xl border border-dashed border-slate-700 p-6 text-center text-sm text-slate-500">
        暂无交付结果,正在获取…
      </p>
    )
  }

  const onCopy = async () => {
    try {
      await navigator.clipboard?.writeText(result)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // 剪贴板不可用时静默
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800">
      <div className="flex items-center gap-2 border-b border-slate-800 bg-slate-900/40 px-4 py-2">
        <FileText className="h-4 w-4 text-indigo-400" />
        <span className="text-sm font-medium">交付结果</span>
        {/* eslint-disable-next-line react/prop-types */}
        <button
          onClick={onCopy}
          className="ml-auto inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-slate-300 hover:bg-slate-800"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-emerald-400" /> 已复制
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" /> 复制
            </>
          )}
        </button>
      </div>
      <pre className="max-h-96 overflow-auto whitespace-pre-wrap bg-slate-950/50 p-4 font-mono text-xs leading-relaxed text-slate-200">
        {result}
      </pre>
    </div>
  )
}
