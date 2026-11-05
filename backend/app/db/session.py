"""数据库引擎与会话:SQLAlchemy async 模式(asyncpg 驱动)"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()
# create_async_engine:建引擎(连接池),不立即连接
# pool_pre_ping=True:每次取连接前先 ping,防止"死连接"("MySQL/PG server gone away")
# pool_size=5 / max_overflow=10:池 5 个常驻连接,最多临时扩到 15
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# async_sessionmaker:Session 工厂,每次 new() 出一个独立会话
# expire_on_commit=False:commit 后对象不失效(否则 commit 后访问字段会抛错)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """供 FastAPI 依赖注入使用:每请求一个 session,用完自动关闭"""
    # 语法上 yield 让 FastAPI 知道"请求结束后执行清理"
    async with async_session() as session:
        yield session
