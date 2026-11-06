import pytest

from app.db.session import engine


@pytest.fixture(autouse=True)
async def _clean_engine():
    """每次测试前清空连接池。

    ⭐ 为什么需要:pytest 让每个 async 测试用独立事件循环,
      而 async engine 的连接池里,第一个连上来的那个连接会
      "记住"它被创建时的 loop;不清池,下个测试拿到的连接
      还是旧 loop 的 → 报 Event loop is closed。
    """
    await engine.dispose()
    yield
