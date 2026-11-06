"""GET /api/v1/health:路由薄、service 厚"""

from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services.health import health_status

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """健康检查端点"""
    return HealthResponse(**await health_status())
