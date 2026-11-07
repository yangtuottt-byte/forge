"""pytest 共用夹具:事件循环隔离 + 测试间数据隔离"""

import pytest
from sqlalchemy import delete

from app.agents.llm import reset_client
from app.core.redis import redis_client
from app.db.session import async_session, engine
from app.models.user import User


@pytest.fixture(autouse=True)
async def _clean_env():
    """每个测试:
    - 跑前清空连接池(防事件循环串线):engine/redis 清池,llm 重建 client
    - 跑后清空 users 表(测试间数据隔离)
    ⚠️ 只清开发容器里的测试表,生产环境绝不能这么干
    """
    await engine.dispose()
    await redis_client.aclose()
    reset_client()  # ⭐ 重建 LLM client(close 后不能复用,重建 = 全新连接池)
    yield
    # 测试结束:清空 users,下一个测试从干净状态开始
    async with async_session() as session:
        await session.execute(delete(User))
        await session.commit()
    await engine.dispose()
    await redis_client.aclose()
