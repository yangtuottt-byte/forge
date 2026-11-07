"""用户业务逻辑:注册、登录"""
import json
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


async def get_user_me(session: AsyncSession, user_id: int) -> dict:
    """查询当前用户(带缓存):先查 redis,miss 查 DB 再回填缓存 key = user:{id},TTL 60s"""
    from app.core.cache import cache_get,cache_set
    key = f"user:{user_id}"
    cached = await cache_get(key)
    if cached:
        return json.loads(cached)
    user = await user_repo.get_by_id(session, user_id)
    data = {"id": user.id, "email": user.email, "role": user.role}
    await cache_set(key, json.dumps(data), ttl=60)
    return data
