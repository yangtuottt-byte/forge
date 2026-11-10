"""
实时进度:WebSocket 连接管理 + Redis pub/sub 桥接

原理:Worker 和 API 是不同进程,跨进程通信用 Redis pub/sub
Worker publish 进度 → Redis → API 订阅 → 转发给 WebSocket
"""

import json

from app.core.redis import redis_client

# task_id -> WebSocket 连接
connections: dict[int, object] = {}


async def connect(websocket, task_id: int) -> None:
    """WebSocket 连接:注册到连接池"""
    await websocket.accept()
    connections[task_id] = websocket


async def disconnect(task_id: int) -> None:
    """断开连接"""
    connections.pop(task_id, None)


async def publish_progress(task_id: int, status: str, progress: int, client=None) -> None:
    """Worker端:推送进度到Redis频道

    ⭐ client:Worker 每次任务新建(每任务独立连接,绑定当前事件循环);
    不传则用 API 进程的模块级单例
    """
    redis = client if client is not None else redis_client
    await redis.publish(
        f"task:{task_id}", json.dumps({"status": status, "progress": progress})
    )


async def subscribe_and_forward(websocket, task_id: int) -> None:
    """API 端:订阅 Redis 频道,转发给 WebSocket"""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"task:{task_id}")
    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await websocket.send_json(json.loads(msg["data"]))
    finally:
        await pubsub.unsubscribe(f"task:{task_id}")
        await pubsub.aclose()
