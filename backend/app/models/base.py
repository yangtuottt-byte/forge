"""模型基类:所有 ORM 模型继承它(Alembic/SQLAlchemy 靠它收集表定义)"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 风格基类"""
