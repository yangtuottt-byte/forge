"""Redis 客户端:全局单例 + 连接池"""

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()

# redis.asyncio:异步客户端
# decode_responses=True:自动把 bytes 转 str,省 decode 步骤


def new_redis_client() -> aioredis.Redis:
    """新建独立客户端(连接池独立,用完自行 aclose)

    ⭐ 供 Worker 任务等"每次 asyncio.run 新事件循环"的场景用:
    模块级 redis_client 的连接池只能绑定在"首次使用它的那个事件循环"上,
    跨循环复用会报 Event loop is closed / attached to a different loop。
    """
    return aioredis.from_url(settings.redis_url, decode_responses=True, max_connections=20)


# API 进程(单个常驻事件循环)用的全局单例
redis_client = new_redis_client()
