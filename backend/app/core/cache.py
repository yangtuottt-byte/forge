"""缓存读写 + 分布式锁"""

from app.core.redis import redis_client


async def cache_get(key: str) -> str | None:
    """读缓存,None=没命中"""
    return await redis_client.get(key)


async def cache_set(key: str, value: str, ttl: int = 60) -> None:
    """写缓存 + 过期秒数"""
    await redis_client.set(key, value, ex=ttl)


async def cache_delete(key: str) -> None:
    """删缓存"""
    await redis_client.delete(key)


async def acquire_lock(name: str, expire: int = 10, client=None) -> bool:
    """
    分布式锁:SET key value NX EX ttl 原子抢锁
    返回 True=抢到,False=已被别人抢走(不用先 check 再 set)

    ⭐ client:可传入调用方自建的 Redis 客户端(Worker 每次任务新建,
      避开模块级单例跨事件循环复用);不传则用 API 进程的模块级单例
    """
    redis = client if client is not None else redis_client
    return bool(await redis.set(name, "locked", nx=True, ex=expire))


async def release_lock(name: str, client=None) -> None:
    redis = client if client is not None else redis_client
    await redis.delete(name)
