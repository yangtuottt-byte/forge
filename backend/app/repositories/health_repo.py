"""repository 层:唯一直接碰数据库的地方"""

from sqlalchemy import text

from app.db.session import async_session


async def check_database() -> bool:
    """探活数据库(其他层不碰 SQL,这里是唯一入口)"""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
