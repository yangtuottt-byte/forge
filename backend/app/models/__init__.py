from app.models.base import Base
from app.models.user import User

# Base.metadata 是由 Base 类管理的全局表注册表
__all__ = ["Base", "User"]
