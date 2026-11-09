import { useEffect, useRef, useState } from 'react'
import { getToken } from '../api/client'
import { getTask } from '../api/tasks'
import { API_BASE, toWsBase } from '../lib/apiBase'
import type { TaskProgressEvent, TaskStatus } from '../api/types'

// 把 API 基础地址转成可连接的 ws:// URL
// - dev:API_BASE 是绝对 http://localhost:8000/api/v1 → ws://localhost:8000/api/v1
// - prod:API_BASE 是相对路径(/api/v1),取当前页面 host 拼 ws(s)://host/api/v1
function wsUrlFor(taskId: number): string {
  const path = `/tasks/${taskId}/ws`
  if (/^https?:\/\//i.test(API_BASE)) return toWsBase(API_BASE) + path
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}${API_BASE}${path}`
}

interface UseTaskProgressOptions {
  onFinished?: () => void
}

export interface UseTaskProgressReturn {
  status: TaskStatus
  progress: number
}

// 实时进度 hook:订阅 WS /tasks/{id}/ws?token=...,收 {status,progress}
// 能力:指数退避重连(worker/Redis 抖动不断体验)、done/failed 收口关闭、
//        启动时先 GET 一次同步当前状态(防任务已先完成而错过订阅)
export function useTaskProgress(
  taskId: number | null,
  opts: UseTaskProgressOptions = {},
): UseTaskProgressReturn {
  const [status, setStatus] = useState<TaskStatus>('pending')
  const [progress, setProgress] = useState(0)
  const onFinishedRef = useRef(opts.onFinished)
  onFinishedRef.current = opts.onFinished // 始终拿最新回调,避免闭包过期
  const finishedRef = useRef(false)

  useEffect(() => {
    if (taskId == null) return
    finishedRef.current = false
    setStatus('pending')
    setProgress(0)

    let ws: WebSocket | null = null
    let retry = 0
    let timer: ReturnType<typeof setTimeout> | null = null
    let closed = false

    // 完成/失败收口:标记、回调、关闭连接(此后 onclose 不再重连)
    const onFinish = (st: TaskStatus) => {
      finishedRef.current = true
      onFinishedRef.current?.()
      setStatus(st)
      if (ws) ws.close()
    }

    const connect = () => {
      if (closed) return
      const token = encodeURIComponent(getToken() ?? '')
      ws = new WebSocket(`${wsUrlFor(taskId)}?token=${token}`)

      ws.onopen = () => {
        retry = 0
        // 订阅前先拉一次真实状态:任务若已先 done/failed 也不会卡在 pending
        void getTask(taskId)
          .then((t) => {
            setStatus(t.status)
            setProgress(t.progress)
            if (t.status === 'done' || t.status === 'failed') onFinish(t.status)
          })
          .catch(() => {})
      }
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data as string) as TaskProgressEvent
          setStatus(data.status)
          setProgress(data.progress)
          if (data.status === 'done' || data.status === 'failed') onFinish(data.status)
        } catch {
          // 忽略非本协议帧
        }
      }
      ws.onclose = () => {
        if (closed || finishedRef.current) return
        // 异常断开:指数退避重连,上限 10s
        const delay = Math.min(1000 * 2 ** retry, 10000)
        retry += 1
        timer = setTimeout(connect, delay)
      }
    }

    connect()

    return () => {
      closed = true
      if (timer) clearTimeout(timer)
      if (ws) ws.close()
    }
  }, [taskId])

  return { status, progress }
}
