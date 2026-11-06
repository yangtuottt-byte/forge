"""用户数据访问:CRUD"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """按邮箱查用户(登录注册都用它)"""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    """按 id 查用户(JWT 验证后用它拿当前用户)"""
    return await session.get(User, user_id)


async def create_user(
    session: AsyncSession, email: str, password_hash: str, role: str = "user"
) -> User:
    """插一行(自增 id,password 存哈希)"""
    user = User(email=email, password_hash=password_hash, role=role)
    session.add(user)
    await session.commit()
    await session.refresh(user)  # 拿回来自增 id(否则 id 是 None)
    return user
