"""用户路由:GET /api/v1/users/me"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut
from app.services.user_service import get_user_me
router = APIRouter()


@router.get("/me", response_model=UserOut)
async def me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
    ) -> UserOut:
    """带 token 访问:拿当前用户信息"""
    return UserOut(**await get_user_me(session, current_user.id))



