"""
Celery实例:异步任务队列

三组件:broker(redis排队)/worker(执行)/backend(存结果)
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "forge",
    broker=settings.redis_url,  # Broker = Redis(任务排队)
    backend=settings.redis_url,  # Result Backend(存结果)
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    # 让 worker 启动时自动导入任务模块,注册 run_agent_task
    include=["app.workers.tasks"],
)
