# ADR-001:为什么用 Celery 做异步任务队列

## 背景
Agent 任务慢(LLM 调用几分钟),需要异步执行,不能阻塞 API 请求。

## 决策
用 **Celery + Redis(Broker)** 做异步任务队列。

## 理由

| 候选 | 评估 |
|------|------|
| **Celery** ✅ | 生态成熟,功能全(重试/定时/死信/并发/优先级) |
| RQ | 功能少,无死信,无定时 |
| Dramatiq | 生态小,文档少 |
| 直接 asyncio | 无队列,Worker 崩溃任务丢失 |
| RabbitMQ | 功能强但重,Redis 已够(Broker 复用) |

**关键理由**:
1. 功能全面:重试(autoretry)、定时、死信、并发 worker
2. Broker 复用:Redis 既是缓存又是 Broker,减少组件
3. 生态成熟:文档/社区/生产案例多

## 影响
- API 立即返回任务 ID,Worker 后台执行
- 进度通过 Redis pub/sub 推送(WebSocket)
- 任务状态持久化 PostgreSQL(可查/可恢复)
- 可靠性:分布式锁/幂等/重试/死信

## 替代方案(若未来需要)
- 任务量极大 → RabbitMQ/Kafka 做 Broker
- 简单任务 → 直接 asyncio + 后台线程
