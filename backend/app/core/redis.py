"""Redis 客户端:全局单例 + 连接池"""

import redis.asyncio as aioredis
from app.core.config import get_settings

settings = get_settings()

# redis.asyncio:异步客户端
# decode_responses=True:自动把 bytes 转 str,省 decode 步骤

redis_client = aioredis.from_url(
    settings.redis_url,
    decode_responses=True,
    max_connections=20
)
