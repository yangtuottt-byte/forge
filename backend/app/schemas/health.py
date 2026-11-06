"""API响应 schema:约束并序列化响应"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str  # ok / degraded
    db: bool  # 数据库是否可用
