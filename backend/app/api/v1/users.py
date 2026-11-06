"""用户路由:GET /api/v1/users/me"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """带 token 访问:拿当前用户信息"""
    return UserOut.model_validate(current_user)
