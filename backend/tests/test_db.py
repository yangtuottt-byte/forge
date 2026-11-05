"""数据库集成测试:ORM 引擎 → PostgreSQL 真实表"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.db.session import async_session, engine
from app.models.user import User


async def test_insert_and_read_user():
    """环境感知:本地有 PG 就真跑;CI 无库则跳过(不红)"""
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))  # 探活
    except OperationalError:
        pytest.skip("数据库不可用(本地需先 docker compose up pg)")

    async with async_session() as session:
        # 插入一行
        user = User(email="alice@example.com", password_hash="hashed", role="admin")
        session.add(user)
        await session.commit()

        # 读回来(按 id 排序取第一条)
        result = await session.execute(select(User).order_by(User.id))
        row = result.scalars().first()
        assert row.email == "alice@example.com"
        assert row.role == "admin"
        assert row.id is not None  # 自增主键生效

        # 清理:测试自己收拾,保证可重复跑
        await session.delete(row)
        await session.commit()
