"""Redis 集成测试:缓存 + 分布式锁"""

import asyncio

import pytest

from app.core.cache import acquire_lock, cache_delete, cache_get, cache_set, release_lock
from app.core.redis import redis_client


@pytest.fixture(autouse=True)
async def _redis_or_skip():
    """环境感知:Redis 没起就跳过(CI 里没有 redis)
    ⭐ 不能写 scope="module":asyncio_mode=auto 下 async fixture 只支持 function scope"""
    try:
        await redis_client.ping()
    except Exception:
        pytest.skip("Redis 未运行")


async def test_redis_ping():
    await redis_client.ping()  # 不抛异常即通过


async def test_cache_set_get():
    await cache_set("test:key", "value", ttl=60)
    assert await cache_get("test:key") == "value"
    await cache_delete("test:key")
    assert await cache_get("test:key") is None


async def test_distributed_lock():
    """锁互斥:抢到锁后第二个抢不到;释放后又能抢"""
    assert await acquire_lock("test:lock", expire=10) is True
    assert await acquire_lock("test:lock", expire=10) is False  # 已被锁住
    await release_lock("test:lock")
    assert await acquire_lock("test:lock", expire=10) is True
    await release_lock("test:lock")


async def test_cache_ttl():
    """缓存过期:TTL 到期自动消失"""
    await cache_set("test:ttl", "v", ttl=1)
    assert await cache_get("test:ttl") == "v"
    await asyncio.sleep(1.2)
    assert await cache_get("test:ttl") is None
