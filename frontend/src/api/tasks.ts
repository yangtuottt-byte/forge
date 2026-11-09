import { request } from './client'
import type { AgentTask, CreateTaskResponse } from './types'

// 任务接口
// POST /tasks?goal=...  → 创建任务(丢 Celery 队列,立即返回 202 {id, status})
export async function createTask(goal: string): Promise<CreateTaskResponse> {
  const qs = new URLSearchParams({ goal }).toString()
  return request<CreateTaskResponse>(`/tasks?${qs}`, { method: 'POST' })
}

// GET /tasks/{id} → 查询任务状态(结果进度完成后拉取 result 用)
export async function getTask(taskId: number): Promise<AgentTask> {
  return request<AgentTask>(`/tasks/${taskId}`)
}
