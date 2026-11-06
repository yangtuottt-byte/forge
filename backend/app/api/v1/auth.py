"""认证路由:POST /api/v1/auth/register,POST /api/v1/auth/login"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import Token, UserCreate
from app.services.user_service import login, register

router = APIRouter()


@router.post("/register", response_model=Token, status_code=201)
async def register_user(body: UserCreate, session: AsyncSession = Depends(get_db)) -> Token:
    """注册后直接返回 token,前端免二次登录"""
    data = await register(session, body.email, body.password)
    return Token(access_token=data.get("access_token", ""))


@router.post("/login", response_model=Token)
async def login_user(body: UserCreate, session: AsyncSession = Depends(get_db)) -> Token:
    """登录:校验密码 → 签发 token"""
    data = await login(session, body.email, body.password)
    return Token(**data)
