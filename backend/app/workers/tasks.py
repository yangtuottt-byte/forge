import asyncio

from app.agents.orchestrator import Orchestrator
from app.db.session import async_session
from app.models.task import AgentTask
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception), retry_backoff=True, max_retries=3)
def run_agent_task(self, task_id: int) -> str:
    """执行 Agent 任务(Worker 消费)"""

    async def _run():
        async with async_session() as session:
            task = await session.get(AgentTask, task_id)
            task.status = "running"
            task.progress = 10
            await session.commit()

            # 执行agent
            orch = Orchestrator()
            result = await orch.run(task.goal)

            # 更新结果
            task.status = "done"
            task.progress = 100
            task.result = result
            await session.commit()
            return result

    return asyncio.run(_run())
