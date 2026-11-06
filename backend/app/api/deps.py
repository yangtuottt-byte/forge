"""FastAPI 依赖:当前用户 + RBAC 角色校验"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repo import get_by_id

http_bearer = HTTPBearer()


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    """从 Authorization 头解出 JWT → 查用户"""
    if not creds:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = decode_token(creds.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效令牌")
    except Exception:
        # from None:有意吞掉原始异常细节(签名错误/过期等),不暴露给调用方
        raise HTTPException(status_code=401, detail="无效或过期令牌") from None
    user = await get_by_id(session, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_roles(*roles: str):
    """RBAC 工厂:require_roles("admin") → 只有 admin 能进"""

    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="无权限")
        return user

    return dependency
