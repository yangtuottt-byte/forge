# Forge 架构

## 系统全景

```
用户 → API(FastAPI) → 提交任务
  → 丢到 Redis(Broker) → 立即返回任务ID
  → Worker(Celery) 消费执行
    → 规划者/研究员/执行者/审查员(多 Agent 协作)
    → 调 LLM(星火/DeepSeek,OpenAI 兼容)
    → 调工具(搜索/代码执行/文件操作)
  → 进度变化 → Redis pub/sub → API → WebSocket 推送前端
  → 结果持久化 PostgreSQL
```

## 分层

| 层 | 职责 | 技术 |
|----|------|------|
| **API 层** | 路由 + 中间件(限流/日志) | FastAPI |
| **Service 层** | 业务逻辑 | Python |
| **Worker 层** | 异步任务执行 | Celery + Redis |
| **Agent 层** | 多 Agent 协作(规划/研究/执行/审查) | 自研 |
| **工具层** | 搜索/代码执行/文件操作 | MCP 风格 |
| **数据层** | 任务/用户 + 缓存/锁/Broker | PostgreSQL + Redis |

## 关键设计

### 异步执行
- Celery 队列:API 丢任务立即返回,Worker 后台执行
- 任务状态持久化:agent_tasks 表(status/progress/result)

### 实时进度
- Redis pub/sub:Worker 推进度 → API 订阅 → WebSocket 推送前端
- 跨进程通信:Worker 和 API 不同进程,用 Redis 桥接

### 可靠性
- 分布式锁:SET NX EX 防重复执行
- 幂等:task_id + 状态检查
- 重试:Celery autoretry(max_retries=3)
- 死信:重试耗尽 status=failed,人工处理

### 安全
- 代码沙箱:subprocess + 超时(生产加固 namespace+seccomp)
- 路径白名单:只允许 workspace 下文件
- 限流:滑动窗口中间件
- 认证:JWT + bcrypt + RBAC

### 可观测
- 结构化日志:JSON 格式
- 限流感知:LLM 测试限流 skip

## 部署

- Docker Compose:API + Worker + PG + Redis 一键起
- 容器间通信:服务名(DB_HOST=pg)
- 配置:.env 注入,密钥不入库
