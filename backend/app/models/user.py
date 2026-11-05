from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"  # 表名
    id: Mapped[int] = mapped_column(primary_key=True)  # 自增主键
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # 邮箱唯一+索引
    password_hash: Mapped[str] = mapped_column(String(255))  # 存 bcrypt 哈希,不存明文
    role: Mapped[str] = mapped_column(String(32), default="user")  # RBAC 角色:user/admin

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
