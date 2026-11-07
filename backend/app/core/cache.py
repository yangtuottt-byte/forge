"""缓存读写 + 分布式锁"""
from app.core.redis import redis_client

async def cache_get(key:str) -> str | None:
    """读缓存,None=没命中"""
    return await redis_client.get(key)

async def cache_set(key: str, value: str, ttl: int = 60) -> None:
    """写缓存 + 过期秒数"""
    await redis_client.set(key, value, ex=ttl)

async def cache_delete(key: str) -> None:
    """删缓存"""
    await redis_client.delete(key)

async def acquire_lock(name: str, expire: int = 10) -> bool:
    """
    分布式锁:SET key value NX EX ttl 原子抢锁
    返回 True=抢到,False=已被别人抢走(不用先 check 再 set)
    """
    return bool(await redis_client.set(name, "locked", nx=True, ex=expire))

async def release_lock(name: str) -> None:
    await redis_client.delete(name)

