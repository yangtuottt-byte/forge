from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.task import AgentTask
from app.realtime.hub import connect, disconnect, subscribe_and_forward
from app.workers.tasks import run_agent_task

router = APIRouter()


@router.post("/tasks", status_code=202)
async def create_task(goal: str, session: AsyncSession = Depends(get_db)) -> dict:
    """提交任务(异步):丢到 Celery 队列,立即返回任务ID"""
    task = AgentTask(goal=goal, status="pending")
    session.add(task)
    await session.commit()
    await session.refresh(task)
    run_agent_task.delay(task.id)  # ⭐ 丢到队列,Worker 后台执行
    return {"id": task.id, "status": task.status}


@router.get("/tasks/{task_id}")
async def get_task(task_id: int, session: AsyncSession = Depends(get_db)) -> dict:
    """查询任务状态"""
    task = await session.get(AgentTask, task_id)
    if not task:
        return {"error": "任务不存在"}
    return {
        "id": task.id,
        "goal": task.goal,
        "status": task.status,
        "progress": task.progress,
        "result": task.result,
    }


@router.websocket("/tasks/{task_id}/ws")
async def task_ws(websocket: WebSocket, task_id: int):
    """WebSocket:实时进度推送"""
    await connect(websocket, task_id)
    try:
        await subscribe_and_forward(websocket, task_id)
    finally:
        await disconnect(task_id)
