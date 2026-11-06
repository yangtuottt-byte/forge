"""用户业务逻辑:注册、登录"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories import user_repo


async def register(session: AsyncSession, email: str, password: str) -> dict:
    """注册:邮箱查重 → 哈希密码 → 落库"""
    if await user_repo.get_by_email(session, email):
        raise HTTPException(status_code=400, detail="邮箱已注册")
    user = await user_repo.create_user(session, email, hash_password(password))
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


async def login(session: AsyncSession, email: str, password: str) -> dict:
    """登录:查用户 → 检验密码 → 签发 JWT"""
    user = await user_repo.get_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
