"""API v1 路由汇总:所有子路由挂到这一个 api_router 上"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
