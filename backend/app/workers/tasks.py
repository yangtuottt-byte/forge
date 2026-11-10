import asyncio

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.agents.llm import reset_client
from app.agents.orchestrator import Orchestrator
from app.core.cache import acquire_lock, release_lock
from app.core.config import get_settings
from app.core.redis import new_redis_client
from app.models.task import AgentTask
from app.realtime.hub import publish_progress
from app.workers.celery_app import celery_app

settings = get_settings()


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def run_agent_task(self, task_id: int) -> str:
    """执行 Agent 任务(Worker 消费)"""
    asyncio.run(_run(task_id))


async def _run(task_id: int) -> str:
    """单个任务完整执行体

    ⭐ 为什么每次任务都要新建 engine / redis / LLM client:
    Celery 的 sync task 每次调用 asyncio.run() 都会创建"新事件循环",
    而模块级全局(session.engine 连接池 / redis_client / llm.client)会绑定
    "首次使用它的那个循环":第一次跑绑定 loopA,重试/下一个任务跑 loopB 时
    连接池里全是 loopA 的连接 → "Event loop is closed"/"attached to a different loop"。
    解法:每次执行体自己建、用完销毁,不跨循环复用。
    """
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    redis = new_redis_client()
    reset_client()  # 重建 LLM client → 绑定当前循环的连接池

    try:
        async with session_factory() as session:
            task = await session.get(AgentTask, task_id)
            # 幂等:已done 不重跑
            if task.status == "done":
                return task.result
            # 分布式锁:防重复执行
            lock = await acquire_lock(f"task:{task_id}", expire=600, client=redis)
            if not lock:
                return "任务正在被其他 worker 执行"
            try:
                task.status = "running"
                task.progress = 10
                await session.commit()
                # 推送进度到 Redis
                await publish_progress(task_id, "running", 10, client=redis)

                # 执行agent
                orch = Orchestrator()
                result = await orch.run(task.goal)

                # 更新结果
                task.status = "done"
                task.progress = 100
                task.result = result
                await session.commit()
                await publish_progress(task_id, "done", 100, client=redis)
                return result
            except Exception:
                task.status = "failed"
                await session.commit()
                raise  # 触发 Celery 重试
            finally:
                await release_lock(f"task:{task_id}", client=redis)
    finally:
        await engine.dispose()
        await redis.aclose()
