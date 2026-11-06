"""
FastAPI 入口:app + 生命周期(lifespan)
- lifespan:应用启动/关闭时执行钩子(预热缓存、释放引擎)
- 挂载所有路由
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """上下文管理器:yield 之前 = 启动逻辑,之后 = 关闭逻辑"""
    print(f"{settings.app_name} starting...")
    yield  # 应用运行中(所有请求在这里响应)
    # 关闭:释放连接池
    await engine.dispose()
    print(f"{settings.app_name} stopped")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(api_router, prefix="/api/v1")
