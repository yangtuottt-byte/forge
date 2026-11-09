// 与后端 schema 对齐的请求 / 响应类型
// 注意:后端 TaskStatus 当前实际为 pending / running / done / failed

export type TaskStatus = 'pending' | 'running' | 'done' | 'failed'

export interface UserCreate {
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface UserOut {
  id: number
  email: string
  role: string
}

export interface CreateTaskResponse {
  id: number
  status: TaskStatus
}

export interface AgentTask {
  id: number
  goal: string
  status: TaskStatus
  progress: number // 0-100
  result: string
}

// WebSocket 推送的进度事件(后端 publish_progress: {status, progress})
export interface TaskProgressEvent {
  status: TaskStatus
  progress: number
}
